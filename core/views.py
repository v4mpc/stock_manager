from datetime import date
from dataclasses import dataclass

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group, User
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, ListView
from django.views.generic.edit import UpdateView
from django.db import transaction
import arrow
from ajax_datatable.views import AjaxDatatableView

from .ajax_datatable_views import ProductSaleAjaxDatatableView
from .forms import (
    AdminResetPasswordForm,
    CustomUserCreationForm,
    ProductCreateForm,
    RoleForm,
    UserModelForm,
    SaleForm,
    UserProfileForm, ReceiveForm, AdjustForm, ExpenseForm

)

from core.util import *

from .models import Product, Unit, StockOnHand

User = get_user_model()

report_list = [{
    'product_sales': {}
}]

reports = [
    ('core:product-sales', 'Product Sales Report'),
    ('core:expenses', 'Expenses Report')
]


@dataclass
class Report:
    name: str
    link: str


def login_success(request):
    # if request.user.home_zone:
    #
    #     if request.user.home_zone.code != "TZ":
    #         return redirect("/dashboard/zonal")
    #     else:
    return render(request, "dashboard.html")
    # else:
    # raise PermissionDenied()


def report_view(request):
    rep = [Report(y, x) for x, y in reports]
    print(rep)
    context = {'reports': rep}
    return render(request, "reports/list.html", context=context)


def product_sales(request):
    return render(request, "reports/product_sales.html", context={})


def expenses(request):
    return render(request, "reports/expenses.html", context={})


def index_view(request):
    return render(request, "index.html")


class UserCreateView(
    PermissionRequiredMixin, LoginRequiredMixin, SuccessMessageMixin, CreateView
):
    template_name = "users/add.html"
    form_class = CustomUserCreationForm
    permission_required = ("core.add_user",)
    success_message = "User saved!"

    def get_success_url(self):
        return reverse("core:user-list")


class RoleCreateView(
    PermissionRequiredMixin, SuccessMessageMixin, CreateView, LoginRequiredMixin
):
    template_name = "roles/add.html"
    form_class = RoleForm
    permission_required = ("auth.add_group",)
    success_message = "Role saved!"

    def get_success_url(self):
        return reverse("core:role-list")


class UserUpdateProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "users/add.html"
    form_class = UserProfileForm
    success_message = "User saved!"

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs["pk"])
        if user.id == self.request.user.id:
            return User.objects.all()
        else:
            raise Http404()

    def get_success_url(self):
        return self.request.path_info


class UserUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "users/add.html"
    # queryset = User.objects.all()
    form_class = UserModelForm

    # permission_required = ("auth.update_user",)

    def get_success_url(self):
        return reverse("core:user-list")

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs["pk"])
        print(user.id)
        print(self.request.user.id)
        if (
                self.request.user.has_perm("core.update_user")
                or user.id == self.request.user.id
        ):
            return User.objects.all()
        else:
            raise Http404()


class RoleUpdateView(
    PermissionRequiredMixin, LoginRequiredMixin, SuccessMessageMixin, UpdateView
):
    template_name = "roles/add.html"
    queryset = Group.objects.all()
    form_class = RoleForm
    permission_required = ("auth.change_group",)
    success_message = "Role saved!"

    def get_success_url(self):
        return reverse("core:role-list")


class UserListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    template_name = "users/list.html"
    queryset = User.objects.all()
    context_object_name = "users"
    permission_required = ("core.view_user",)


class ProductListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    template_name = "products/list.html"
    queryset = Product.objects.all()
    context_object_name = "products"
    permission_required = ("core.view_product",)


class ProductCreateView(
    PermissionRequiredMixin, SuccessMessageMixin, CreateView, LoginRequiredMixin
):
    template_name = "products/add.html"
    form_class = ProductCreateForm
    permission_required = ("auth.add_product",)
    success_message = "Role saved!"

    def get_success_url(self):
        return reverse("core:product-list")


class ReceiveCreateView(
    PermissionRequiredMixin, SuccessMessageMixin, CreateView, LoginRequiredMixin
):
    template_name = "receive/add.html"
    form_class = ReceiveForm
    permission_required = ("auth.add_product",)
    success_message = "Transaction saved!"

    def get_form_kwargs(self):
        kwargs = super(ReceiveCreateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        update_stock_on_hand(form.instance.product, date.today(), form.instance.quantity, 'DR')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("core:receive")


class StockAdjustCreateView(
    PermissionRequiredMixin, SuccessMessageMixin, CreateView, LoginRequiredMixin
):
    template_name = "soh/add.html"
    form_class = AdjustForm
    permission_required = ("auth.add_product",)
    success_message = "Transaction saved!"

    def get_form_kwargs(self):
        kwargs = super(StockAdjustCreateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        kwargs.update({'pk': self.kwargs['pk']})
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        tx = 'DR'
        if form.instance.quantity < 0:
            tx = 'CR'
        update_stock_on_hand(form.instance.product, date.today(), form.instance.quantity, tx)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("core:stock_on_hand")


class StockSaleCreateView(
    PermissionRequiredMixin, SuccessMessageMixin, CreateView, LoginRequiredMixin
):
    template_name = "soh/sale.html"
    form_class = SaleForm
    permission_required = ("auth.add_product",)
    success_message = "Transaction saved!"

    def get_form_kwargs(self):
        kwargs = super(StockSaleCreateView, self).get_form_kwargs()
        self.product = Product.objects.get(pk=self.kwargs['pk'])
        kwargs.update({'request': self.request})
        kwargs.update({'product': self.product})
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        tx = 'CR'
        update_stock_on_hand(self.product, date.today(), form.instance.quantity, tx)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("core:stock_on_hand")


class ProductUpdateView(
    PermissionRequiredMixin, LoginRequiredMixin, SuccessMessageMixin, UpdateView
):
    template_name = "products/add.html"
    queryset = Product.objects.all()
    form_class = ProductCreateForm
    permission_required = ("auth.change_product",)
    success_message = "Product saved!"

    def get_success_url(self):
        return reverse("core:product-list")


class RoleListView(PermissionRequiredMixin, ListView, LoginRequiredMixin):
    template_name = "roles/list.html"
    queryset = Group.objects.all()
    context_object_name = "roles"
    permission_required = ("auth.view_group",)


class ExpenseCreateView(
    PermissionRequiredMixin, SuccessMessageMixin, CreateView, LoginRequiredMixin
):
    template_name = "expenses/add.html"
    form_class = ExpenseForm
    permission_required = ("auth.add_group",)
    success_message = "Role saved!"

    def get_success_url(self):
        return reverse("core:expense")


def stock_on_hand_view(request):
    products = Product.objects.all()
    today = arrow.now().today()
    sohs = []
    for p in products:
        model_soh = get_stock_on_hand(p, today)
        sohs.append({'product': p.name, 'product_id': p.pk, 'unit': p.unit_of_measure.code, 'quantity': model_soh})
        context = {'sohs': sohs}
    return render(request, "soh/list.html", context)


def adjust_stock_view(request, pk):
    pass


def dashboard_view(request):
    # selected_dashboard_key = selected_dashboard_key.lower()
    # available_keys = dashboard_mapper.keys()
    # if selected_dashboard_key not in available_keys:
    #     raise Http404
    #
    # context = {
    #     "superset_report_url": dashboard_mapper[selected_dashboard_key],
    # }
    return render(request, "dashboard.html")


# @permission_required("auth.change_user")
def admin_reset_user_password(request, pk):
    user = get_object_or_404(User, pk=pk)

    if not request.user.has_perm("core.update_user") and user.id != request.user.id:
        raise Http404()

    if request.method == "POST":
        form = AdminResetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["password1"])
            user.save()
            messages.success(request, "Password updated!")
            return redirect(request.path_info)
    else:
        form = AdminResetPasswordForm(initial={"username": user.username})
    context = {"username": user.username, "form": form}
    return render(request, "registration/password_change_form.html", context)


def handler404(request, *args, **argv):
    return render(request, "404.html", {})


def handler500(request, *args, **argv):
    pass
    # response = render_to_response('500.html', {},
    #                               context_instance=RequestContext(request))
    # response.status_code = 500
    # return response
