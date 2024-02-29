
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UsernameField,
)
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.forms import ModelForm, ModelMultipleChoiceField
from django_select2 import forms as s2forms

from django.contrib.auth.models import AbstractUser, User
from .util import generate_download_sample_names

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
    "upload_document",
    "view_dashboard",
    "view_reports",
    "view_integration_status",
    "add_group",
    "change_group",
    "view_group",
    "add_user",
    "change_user",
    "view_user",
    "add_geographiczone",
    "change_geographiczone",
    "view_geographiczone",
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

    # username = forms.CharField(max_length=100, disabled=True, required=False)
    # password = forms.CharField(
    #     strip=False,
    #     widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    #     help_text=password_validators_help_text_html(),
    # )
    #
    # def clean(self):
    #     cleaned_data = super().clean()
    #     password = cleaned_data.get("password")
    #     validate_password(password)


