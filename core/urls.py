from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.views.generic import RedirectView

from .views import (

    RoleCreateView,
    RoleListView,
    RoleUpdateView,
    UserCreateView,
    UserListView,
    UserUpdateProfileView,
    UserUpdateView,
    admin_reset_user_password,
    dashboard_view,
    login_success,
    report_detail,
    report_view,
    resource_view,
)

app_name = "core"
urlpatterns = [

    # path('login/', views.LoginView.as_view(authentication_form=CustomAuthenticationForm), name='login'),
    path("dashboard/<str:selected_dashboard_key>", dashboard_view, name="dashboard"),
    path("reports/", report_view, name="reports"),
    path("resources/", resource_view, name="resources"),
    path(
        "reports/<str:selected_report_type>/<str:selected_report_key>",
        report_detail,
        name="report-detail",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/add/", UserCreateView.as_view(), name="user-add"),
    path("roles/", RoleListView.as_view(), name="role-list"),
    path("roles/add/", RoleCreateView.as_view(), name="role-add"),
    path(
        "users/reset-password/<int:pk>/",
        admin_reset_user_password,
        name="user-admin-reset-password",
    ),
    path("users/<int:pk>/update/", UserUpdateView.as_view(), name="user-update"),
    path(
        "user-profile/<int:pk>/", UserUpdateProfileView.as_view(), name="user-profile"
    ),
    path("roles/<int:pk>/update/", RoleUpdateView.as_view(), name="role-update"),

]
