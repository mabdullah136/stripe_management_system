from django.contrib import admin

from customer.models import Customer
from subscriptions.models import Subscription


class SubscriptionInline(admin.StackedInline):
    """
    Inline admin for managing a customer's subscription directly within the CustomerAdmin panel.
    """
    model = Subscription
    extra = 0  # Prevents empty extra forms
    readonly_fields = ("stripe_subscription_id", "status", "last_billed_at", "next_billing_at")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing customers.
    """
    list_display = ("first_name", "last_name", "email", "phone_number", "created_at")
    search_fields = ("first_name", "last_name", "email", "phone_number")
    inlines = [SubscriptionInline]
