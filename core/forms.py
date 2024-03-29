from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UsernameField,
)
from django.contrib.auth.models import Group, Permission, User
from django.core.exceptions import ValidationError
import arrow
from django.forms import ModelForm, ModelMultipleChoiceField, HiddenInput, ChoiceField, ModelChoiceField
from django_select2 import forms as s2forms
from .models import Product, StockCard, StockOnHand, Sale, Expense, Unit
from django.core.exceptions import ValidationError
from .util import get_stock_on_hand

STOCK_STATUS = "SS"
FILE_UPLOAD_CHOICES = [
    (STOCK_STATUS, "Stock Status"),
]
TITLE_CHOICES = [
    ("MR", "Mr."),
    ("MRS", "Mrs."),
    ("MS", "Ms."),
]

PERMISSIONS_TO_SHOW = [
    "view_dashboard",
    "view_reports",
    "add_group",
    "change_group",
    "view_group",
    "add_user",
    "change_user",
    "view_user"
]


class MyModelChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class PermissionSelect(s2forms.Select2MultipleWidget):
    def label_from_instance(self, obj):
        return "My Object #%i" % obj.id

    def create_option(
            self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        if value:
            option["attrs"]["data-name"] = value.instance.name
        return option


class GroupsWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = ["name__icontains"]


class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
        )


class UserModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserModelForm, self).__init__(*args, **kwargs)
        self.fields["groups"].label = "Roles"
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

    class Meta:
        widgets = {
            "groups": s2forms.Select2MultipleWidget,
        }
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_superuser",
            "groups",
        )


# class UserProfileExtraForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ("phone", "zone")


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields["groups"].label = "Roles"
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True

    class Meta:
        widgets = {
            "groups": s2forms.Select2MultipleWidget,
        }
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_superuser",
            "groups",
        )
        field_classes = {"username": UsernameField}

    def save(self, commit=True):
        user = super().save(commit)
        groups = self.cleaned_data.get("groups")
        for gr in groups:
            g = Group.objects.get(name=gr)
            g.user_set.add(user)


class UnitCreateForm(ModelForm):
    class Meta:
        model = Unit
        fields = ["code", "name"]


class ProductCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProductCreateForm, self).__init__(*args, **kwargs)
        self.fields[
            "active"].help_text = "Designates whether Product should show on  Adjustment, Buy, Sell and Stock on hand."

    class Meta:
        model = Product
        fields = ["name", "sale_price", "buy_price", "active", "description", "unit_of_measure"]

    def clean_active(self):
        print(self.instance)
        active = self.cleaned_data["active"]
        # if not self.instance:
        #     return active
        #
        # soh = get_stock_on_hand(self.instance, arrow.now().today())
        # if soh > 0:
        #     raise ValidationError(f"Product has stock of {soh}. Adjust/Sell to deactivate.")

        return active


class AdjustForm(ModelForm):
    stock_on_hand = forms.FloatField()

    class Meta:
        model = StockCard
        fields = ["product", "quantity", "description", "transaction_type", "created_by"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.pk = kwargs.pop("pk")
        self.product = Product.objects.get(pk=self.pk)
        self.soh = get_stock_on_hand(self.product, arrow.now().today())
        super(AdjustForm, self).__init__(*args, **kwargs)
        # we can do better here, hiding forms input is not so secure, these fields should be added from backend on form submission
        self.fields["description"].label = "Adjustment Reason"
        self.fields["quantity"].label = f"Quantity to adjust({self.product.unit_of_measure.code})"
        self.fields[
            "quantity"].help_text = "Negative(-) value will decrease stock e.g -80, Positive value will increase stock e.g 80."
        self.fields["transaction_type"].initial = "DR"
        self.fields["transaction_type"].disabled = True
        self.fields['transaction_type'].widget = HiddenInput()
        self.fields["created_by"].initial = self.request.user
        self.fields["created_by"].disabled = True
        self.fields['created_by'].widget = HiddenInput()
        self.fields["stock_on_hand"].initial = self.soh
        self.fields["stock_on_hand"].label = f"Stock on hand({self.product.unit_of_measure.code})"
        self.fields["stock_on_hand"].help_text = f"Stock on hand as of now({arrow.now().format('YYYY-MM-DD,HH:mm')})."
        self.fields["stock_on_hand"].disabled = True
        self.fields['product'].initial = self.product
        self.fields["product"].disabled = True

    def clean_quantity(self):
        data = self.cleaned_data["quantity"]
        if data == 0.0:
            raise ValidationError("Adjustment can not be zero")
        if (data + self.soh) < 0:
            raise ValidationError("Can not adjust more than available.")
        return data


class ProductSelectWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "name__icontains",
        "description__icontains",
    ]


class DateInput(forms.DateInput):
    input_type = 'date'


class ReceiveForm(ModelForm):
    # stock_on_hand = forms.FloatField()

    class Meta:
        model = StockCard
        fields = ["created_at", "product", "quantity", "description", "transaction_type", "created_by"]
        widgets = {'created_at': DateInput()}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ReceiveForm, self).__init__(*args, **kwargs)
        # we can do better here, hiding forms input is not so secure, these fields should be added from backend on form submission
        self.fields["description"].initial = "RECEIVE"
        choices = Product.objects.filter(active=True)
        self.fields["product"] = ModelChoiceField(queryset=choices, widget=ProductSelectWidget)
        self.fields["quantity"].label = "Quantity to buy"
        self.fields["created_at"].label = "Date"
        self.fields["quantity"].help_text = "Increase stock amount for selected product."
        self.fields["description"].disabled = True
        self.fields['description'].widget = HiddenInput()
        self.fields["transaction_type"].initial = "DR"
        self.fields["transaction_type"].disabled = True
        self.fields['transaction_type'].widget = HiddenInput()
        self.fields["created_by"].initial = self.request.user
        self.fields["created_by"].disabled = True
        self.fields['created_by'].widget = HiddenInput()
        # self.fields["stock_on_hand"].initial = 0.0
        # self.fields["stock_on_hand"].disabled = True

    def clean_quantity(self):
        data = self.cleaned_data["quantity"]
        if data <= 0.0:
            raise ValidationError("Quantity must be greater than zero(0)")
        return data


class RoleForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        self.fields["permissions"].required = True
        self.fields["permissions"] = MyModelChoiceField(
            queryset=Permission.objects.filter(codename__in=PERMISSIONS_TO_SHOW),
            widget=s2forms.Select2MultipleWidget,
        )

    class Meta:
        widgets = {
            "permissions": PermissionSelect,
        }
        model = Group
        fields = ["name", "permissions"]


class AdminResetPasswordForm(UserCreationForm):

    # password = forms.CharField(
    #     strip=False,
    #     widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    #     help_text=password_validators_help_text_html(),
    # )

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields["username"].disabled = True
        self.fields["username"].required = False
        self.fields["username"].help_text = ""

    class Meta:
        model = User
        # exclude = ('first_name',)
        fields = ["username"]


class SaleForm(ModelForm):
    stock_on_hand = forms.FloatField()

    class Meta:
        model = Sale
        fields = ["created_at", "product_name", "buy_price", "sale_price", "quantity", "sale_adjustment", "description"]
        widgets = {'created_at': DateInput()}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        # self.pk = kwargs.pop("pk")
        self.product = kwargs.pop("product")
        self.soh = get_stock_on_hand(self.product, arrow.now().today())
        super(SaleForm, self).__init__(*args, **kwargs)
        # we can do better here, hiding forms input is not so secure, these fields should be added from backend on form submission
        self.fields["description"].label = "Description"
        self.fields["created_at"].label = "Date"
        self.fields["quantity"].label = f"Sale quantity({self.product.unit_of_measure.code})"
        self.fields["quantity"].help_text = "Sale quantity must be greater than Zero(0)"
        self.fields[
            "sale_adjustment"].help_text = "Negative(-) value shall be discount, Positive values shall be Premium sale"
        self.fields["sale_price"].label = "Sale price(TZS)"
        self.fields["buy_price"].label = "Buy price(TZS)"

        self.fields["sale_price"].initial = self.product.sale_price
        self.fields["buy_price"].initial = self.product.buy_price

        self.fields["sale_price"].disabled = True
        self.fields["buy_price"].disabled = True

        # self.fields["created_by"].initial = self.request.user
        # self.fields["created_by"].disabled = True
        # self.fields['created_by'].widget = HiddenInput()
        self.fields["stock_on_hand"].initial = self.soh
        self.fields["stock_on_hand"].disabled = True
        self.fields["stock_on_hand"].label = f"Stock on hand({self.product.unit_of_measure.code})"
        self.fields['product_name'].initial = self.product.name
        self.fields["stock_on_hand"].help_text = f"Stock on hand as of now({arrow.now().format('YYYY-MM-DD,HH:mm')})."
        self.fields["product_name"].disabled = True

    def clean_quantity(self):
        data = self.cleaned_data["quantity"]
        if data <= 0.0:
            raise ValidationError("Sale quantity can not be less or equal to zero")
        if data > self.soh:
            raise ValidationError("Can not sale more than available.")

        return data

    def clean_sale_adjustment(self):
        data = self.cleaned_data["sale_adjustment"]

        if data < 0 and (data * -1) >= self.product.buy_price:
            raise ValidationError("Discount can not be below the buying price")
        return data


class ExpenseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        self.fields["amount"].label = "Amount(TZS)"
        self.fields["created_at"].label = "Date"

    class Meta:
        model = Expense
        fields = ["created_at", "name", "amount", "description"]
        widgets = {'created_at': DateInput()}

    def clean_amount(self):
        data = self.cleaned_data["amount"]
        if data <= 0.0:
            raise ValidationError("Amount must be greater than zero(0)")
        return data
