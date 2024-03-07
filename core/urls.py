from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.views.generic import RedirectView

from . import views
from .ajax_datatable_views import *
from django.contrib.auth.views import LoginView, LogoutView


from .views import *

app_name = "core"
urlpatterns = [

    path("login/", LoginView.as_view(), name="login"),
    # path("login_success/", login_success, name="login_success"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/add/", ProductCreateView.as_view(), name="product-add"),

    path("units/", UnitListView.as_view(), name="unit-list"),
    path("units/add/", UnitCreateView.as_view(), name="unit-add"),
    path("units/<int:pk>/update/", UnitUpdateView.as_view(), name="unit-update"),

    path("receive/", ReceiveCreateView.as_view(), name="receive"),
    path("expense/", ExpenseCreateView.as_view(), name="expense"),
    path("stock_on_hand/", stock_on_hand_view, name="stock_on_hand"),
    path("stock_on_hand/<int:pk>/sale", StockSaleCreateView.as_view(), name="sale_stock"),
    path("stock_on_hand/<int:pk>/adjust_stock", StockAdjustCreateView.as_view(), name="adjust_stock"),
    path("users/add/", UserCreateView.as_view(), name="user-add"),
    path("roles/", RoleListView.as_view(), name="role-list"),
    path("roles/add/", RoleCreateView.as_view(), name="role-add"),
    path(
        "users/reset-password/<int:pk>/",
        admin_reset_user_password,
        name="user-admin-reset-password",
    ),
    path("users/<int:pk>/update/", UserUpdateView.as_view(), name="user-update"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product-update"),
    path(
        "user-profile/<int:pk>/", UserUpdateProfileView.as_view(), name="user-profile"
    ),
    path("roles/<int:pk>/update/", RoleUpdateView.as_view(), name="role-update"),

    # NON AJAX Requests
    path("reports/", report_view, name="reports"),
    path("product-sales/", product_sales, name="product-sales"),
    path("product-sales-aggregate/", product_sales_aggregate, name="product-sales-aggregate"),
    path("expenses/", expenses, name="expenses"),

    # AJAX requests
    path('ajax-product-sales/', ProductSaleAjaxDatatableView.as_view(),
         name="ajax-product-sales"),

    path('ajax-product-sales-aggregate/', ProductSaleAggregateAjaxDatatableView.as_view(),
         name="ajax-product-sales-aggregate"),
    path('ajax-expenses/', ExpenseAjaxDatatableView.as_view(),
         name="ajax-expenses"),

]
