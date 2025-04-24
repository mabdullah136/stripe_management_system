from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.db.models.signals import post_save
from django.dispatch import receiver

import stripe


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Customer(TimeStampedModel):
    # personal details
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    password = models.CharField(max_length=255, blank=True)

    # stripe related fields
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def create_customer(cls, first_name, last_name, email, phone_number, address, password):
        hashed_password = make_password(password)
        return cls.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            address=address,
            password=hashed_password
        )

    def get_or_create_stripe_customer(self):
        if self.stripe_customer_id:
            return self.stripe_customer_id

        existing_customers = stripe.Customer.list(email=self.email).data
        if existing_customers:
            stripe_customer = existing_customers[0]
        else:
            stripe_customer = stripe.Customer.create(
                email=self.email,
                name=f"{self.first_name} {self.last_name}",
                phone=self.phone_number,
            )

        self.stripe_customer_id = stripe_customer.id
        self.save(updated_fields=['stripe_customer_id'])
        return stripe_customer.id

@receiver(post_save, sender=Customer)
def sync_stripe_customer(sender, instance, created, **kwargs):
    if created:  # Only sync when the object is first created
        instance.get_or_create_stripe_customer()
