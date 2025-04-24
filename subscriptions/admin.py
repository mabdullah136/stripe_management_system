from django.contrib import admin
from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """Admin configuration for Plan model."""
    list_display = ("name", "monthly_price", "billing_period")
    search_fields = ("name",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin configuration for Subscription model."""
    list_display = ("customer", "plan", "status", "last_billed_at", "next_billing_at")
    search_fields = ("customer__name", "stripe_subscription_id")
    list_filter = ("status", "plan")

