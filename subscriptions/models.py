import datetime

import stripe
from django.conf import settings
from django.db import models
from django.utils import timezone

from customer.models import Customer


class Plan(models.Model):
    """
    Model representing a subscription plan.
    """

    class BillingPeriodChoices(models.TextChoices):
        MONTHLY = "monthly", "Monthly"

    name = models.CharField(max_length=100, unique=True)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_period = models.CharField(
        max_length=10,
        choices=BillingPeriodChoices.choices,
        default=BillingPeriodChoices.MONTHLY,
        editable=False,
    )

    def __str__(self):
        return f"{self.name} - ${self.monthly_price}/month"


class Subscription(models.Model):
    """
    Model representing a customer's subscription.
    """

    class StatusChoices(models.TextChoices):
        ACTIVE = "active", "Active"
        CANCELED = "canceled", "Canceled"
        PAST_DUE = "past_due", "Past Due"

    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name="subscription")
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="subscriptions")
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    last_billed_at = models.DateTimeField(auto_now_add=True)
    next_billing_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Subscription {self.stripe_subscription_id} - {self.status}"

    @classmethod
    def create_or_update_subscription(
        cls, customer, stripe_subscription_id, last_billed_at, next_billing_at, status=StatusChoices.ACTIVE
    ):
        """
        Creates a new subscription if it doesn't exist, or updates the existing subscription for the given customer.

        Args:
            customer (Customer): The customer associated with the subscription.
            stripe_subscription_id (str): The unique Stripe subscription ID.
            last_billed_at (datetime): Timestamp of the last billing cycle.
            next_billing_at (datetime): Timestamp of the next billing cycle.
            status (str): Subscription status (default: Active).

        Returns:
            tuple: (Subscription object, Boolean indicating whether it was created)
        """
        subscription, created = cls.objects.update_or_create(
            customer=customer,
            defaults={
                "stripe_subscription_id": stripe_subscription_id,
                "status": status,
                "last_billed_at": last_billed_at,
                "next_billing_at": next_billing_at,
            }
        )
        return subscription, created

    def create_stripe_subscription(self, plan, payment_method, promo_code=None, free_trial=False):
        """
        Creates or updates a Stripe subscription for the customer.

        Args:
            plan (Plan): The plan being subscribed to.
            payment_method (PaymentMethod): The customer's payment method (stripe payment method id).
            promo_code (PromoCode, optional): A promotional code for discounts. Defaults to None.
            free_trial (bool, optional): Whether the customer is eligible for a free trial. Defaults to False.

        Returns:
            tuple:
                - success (bool): True if the subscription was created/updated successfully.
                - error_message (str): Error message if any issue occurred, otherwise an empty string.
                - stripe_subscription_id (str or None): The Stripe subscription ID if successful.
                - total_amount (float): The amount charged in the transaction.
        """
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_customer = stripe.Customer.retrieve(self.customer.stripe_customer_id)

        stripe_subscription_id = None

        state = "Started a new subscription"
        if self.stripe_subscription_id:
            stripe_subscription_id = self.stripe_subscription_id
            if self.status == Subscription.StatusChoices.ACTIVE:
                state = "Upgraded"
            elif self.status == Subscription.StatusChoices.CANCELED:
                state = "Reactivated"

        history = f"{state} for plan {plan.name}."
        if free_trial:
            history = f"Started a new subscription for plan {plan.name} from free trial."

        stripe_plan_id = plan.stripe_monthly_plan_id
        current_time_str = str(timezone.now())

        if stripe_subscription_id:
            stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)

            if stripe_subscription and stripe_subscription['status'] != 'canceled':
                existing_meta_data = stripe_subscription.get('metadata', {})
                existing_meta_data[current_time_str] = history
                item_id = stripe_subscription['items']['data'][0]['id']

                stripe_subscription = stripe.Subscription.modify(
                    stripe_subscription_id,
                    items=[{"id": item_id, "price": stripe_plan_id}],
                    expand=["latest_invoice.payment_intent"],
                    trial_end='now',
                    coupon=promo_code,
                    payment_behavior="default_incomplete",
                    proration_behavior='always_invoice',
                    default_payment_method=payment_method,
                    collection_method='charge_automatically',
                    metadata=existing_meta_data
                )
        else:
            stripe_subscription = stripe.Subscription.create(
                customer=stripe_customer.id,
                items=[{'price': stripe_plan_id}],
                coupon=promo_code,
                trial_end=timezone.now() + datetime.timedelta(days=settings.FREE_TRIAL_DAYS) if free_trial else None,
                expand=["latest_invoice.payment_intent"],
                payment_behavior="default_incomplete",
                default_payment_method=payment_method,
                collection_method='charge_automatically',
                metadata={current_time_str: history}
            )

        last_billed_at = timezone.datetime.fromtimestamp(stripe_subscription.get("current_period_start"), tz=timezone.utc)
        next_billing_at = timezone.datetime.fromtimestamp(stripe_subscription.get("current_period_end"), tz=timezone.utc)

        payment_intent = stripe_subscription.latest_invoice.payment_intent
        total_amount = stripe_subscription.latest_invoice.subtotal or 0

        if payment_intent:
            stripe.PaymentIntent.modify(
                payment_intent.id,
                description=f"Subscription Plan [{plan.name}]",
                metadata={"customer_id": self.customer.id, "subscription": True},
            )
            payment_intent = stripe.PaymentIntent.confirm(
                payment_intent.id,
                payment_method=payment_method,
                return_url="https://dashboard.yoursite.com",
            )

            if payment_intent.status != "succeeded":
                return False, payment_intent.last_payment_error.message or "Payment failed.", None, total_amount

        self.stripe_subscription_id = stripe_subscription.id
        self.status = Subscription.StatusChoices.ACTIVE
        self.last_billed_at = last_billed_at
        self.next_billing_at = next_billing_at
        self.save()

        return True, '', stripe_subscription.id, total_amount
