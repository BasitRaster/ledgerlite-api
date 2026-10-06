from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.businesses.models import Business


class Customer(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customers",
    )

    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name


class BusinessCustomer(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="customer_links",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="business_links",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business", "customer"],
                name="unique_business_customer_pair",
            ),
        ]
        ordering = ["id"]

    def clean(self):
        super().clean()

        if not self.business_id or not self.customer_id:
            return

        if self.business.owner_id != self.customer.owner_id:
            raise ValidationError(
                {
                    "customer": (
                        "Business and customer must belong to the same user."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.business} - {self.customer}"
