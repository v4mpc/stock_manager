from django.contrib.auth.models import AbstractUser, User
from django.db import models

MAX_CODE_LENGTH = 100
MAX_NAME_LENGTH = 250

TRANSACTION_TYPES = [("CR", "CREDIT"), ("DR", "DEBIT")]


class RightsSupport(models.Model):
    class Meta:
        managed = False  # No database table creation or deletion
        # operations will be performed for this model.
        default_permissions = ()  # disable "add", "change", "delete"
        # and "view" default permissions
        permissions = (
            ("view_dashboard", "Can view dashboard"),
            ("view_stock_on_hand", "Can view stock on hand"),
            ("view_reports", "Can view reports"),
            ("change_adjustment", "Can adjust stock"),
            ("change_sell", "Can sell stock"),
            ("change_receive", "Can receive stock"),

        )


class Unit(models.Model):
    code = models.CharField(max_length=MAX_CODE_LENGTH, blank=False, unique=True)
    name = models.CharField(max_length=MAX_NAME_LENGTH, blank=False)
    conversion_factor = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "units"
        ordering = ["-id"]

    def __str__(self):
        return self.name


#
# class User(AbstractUser):
#     phone = models.CharField(max_length=20, null=True, blank=True)
#


class Product(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH, blank=False)
    description = models.TextField(null=True, blank=True)
    unit_of_measure = models.ForeignKey(
        "Unit",
        on_delete=models.RESTRICT,
        related_name="units",
    )
    sale_price = models.FloatField()
    buy_price = models.FloatField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class StockCard(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.RESTRICT,
        related_name="products",
    )
    description = models.TextField(null=False, blank=False)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.FloatField()
    created_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="users",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stock_cards"
        ordering = ["-id"]


class Sale(models.Model):
    product_name = models.CharField(max_length=MAX_NAME_LENGTH, blank=False)
    sale_price = models.FloatField()
    buy_price = models.FloatField()
    quantity = models.FloatField()
    description = models.TextField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sales"
        ordering = ["-id"]
        indexes = [
            models.Index(fields=['created_at', 'product_name']),
        ]


class Expense(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH, blank=False)
    description = models.TextField(null=True, blank=True)
    amount = models.FloatField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "expenses"
        ordering = ["-id"]
        indexes = [
            models.Index(fields=['created_at']),
        ]


class StockOnHand(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.RESTRICT
    )
    quantity = models.FloatField()
    created_at = models.DateField()
    updated_at = models.DateField(auto_now=True)

    class Meta:
        db_table = "stock_on_hand"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(fields=['product', 'created_at'], name='unique soh by date')
        ]
        indexes = [
            models.Index(fields=['product', 'created_at', ]),
        ]


class User(AbstractUser):
    phone = models.CharField(max_length=20, null=True, blank=True)
