from django.contrib.auth.models import AbstractUser
from django.db import models


MAX_CODE_LENGTH=100
MAX_NAME_LENGTH=250


class RightsSupport(models.Model):
    class Meta:
        managed = False  # No database table creation or deletion  \
        # operations will be performed for this model.
        default_permissions = ()  # disable "add", "change", "delete"
        # and "view" default permissions
        permissions = (
            ("view_dashboard", "Can view dashboard"),
            ("view_reports", "Can view reports"),
        )



class Unit(models.Model):
    # check on type
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
    code = models.CharField(max_length=MAX_CODE_LENGTH, blank=False, unique=True)
    name = models.CharField(max_length=500, blank=False)
    description = models.TextField(null=True, blank=True)
    unit_of_measure = models.ForeignKey(
        "Unit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        ordering = ["-id"]

    def __str__(self):
        return self.name

