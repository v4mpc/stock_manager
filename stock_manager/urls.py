from django.contrib import admin
from django.contrib.auth.views import PasswordResetView, PasswordChangeView, PasswordResetConfirmView, \
    PasswordResetDoneView, PasswordResetCompleteView, LoginView
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
                  path("", include("core.urls")),
                  path("", RedirectView.as_view(url="login", permanent=True)),
                  path("login/", LoginView.as_view(), name="login"),
                  path("admin/", admin.site.urls),
                  path("select2/", include("django_select2.urls")),
                  path("password-reset/", PasswordResetView.as_view(), name="password-reset"),
                  path(
                      "password-change/",
                      PasswordChangeView.as_view(success_url="users"),
                      name="password_change",
                  ),
                  path(
                      "reset/<uidb64>/<token>/",
                      PasswordResetConfirmView.as_view(),
                      name="password_reset_confirm",
                  ),
                  path(
                      "password-reset/done/",
                      PasswordResetDoneView.as_view(),
                      name="password_reset_done",
                  ),
                  # path('password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
                  path(
                      "reset/done/",
                      PasswordResetCompleteView.as_view(),
                      name="password_reset_complete",
                  )

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
