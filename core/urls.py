from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.views.generic import RedirectView

from .views import *

app_name = "core"
urlpatterns = [

    # path('login/', views.LoginView.as_view(authentication_form=CustomAuthenticationForm), name='login'),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("reports/", report_view, name="reports"),
    path("resources/", resource_view, name="resources"),
    path(
        "reports/<str:selected_report_type>/<str:selected_report_key>",
        report_detail,
        name="report-detail",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/add/", ProductCreateView.as_view(), name="product-add"),
    path("receive/", ReceiveCreateView.as_view(), name="receive"),
    path("stock_on_hand/", stock_on_hand_view, name="stock_on_hand"),
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

]
