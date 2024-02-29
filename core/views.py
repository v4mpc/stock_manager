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

from .forms import (
    AdminResetPasswordForm,
    CustomUserCreationForm,

    RoleForm,
    UserModelForm,
    UserProfileForm,

)

User = get_user_model()

def login_success(request):
    # if request.user.home_zone:
    #
    #     if request.user.home_zone.code != "TZ":
    #         return redirect("/dashboard/zonal")
    #     else:
    return redirect("/dashboard/facility")
    # else:
    # raise PermissionDenied()


def report_view(request):
    context = {"reports": reports_mapper}
    return render(request, "reports/list.html", context=context)


def resource_view(request):
    context = {"resources": resource_mapper}
    return render(request, "resources/list.html", context=context)


def index_view(request):
    return render(request, "index.html")


def report_detail(request, selected_report_type, selected_report_key):
    # TODO check if report key exist
    reports = reports_mapper[selected_report_type]["reports"]
    selected_report = list(filter(lambda r: r["key"] == selected_report_key, reports))[
        0
    ]
    context = {"superset_link": selected_report["superset_link"]}

    return render(request, "reports/detail.html", context=context)


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
    # paginate_by = 10
    context_object_name = "users"
    permission_required = ("core.view_user",)



class RoleListView(PermissionRequiredMixin, ListView, LoginRequiredMixin):
    template_name = "roles/list.html"
    queryset = Group.objects.all()
    context_object_name = "roles"
    permission_required = ("auth.view_group",)



def dashboard_view(request, selected_dashboard_key: str):
    selected_dashboard_key = selected_dashboard_key.lower()
    available_keys = dashboard_mapper.keys()
    if selected_dashboard_key not in available_keys:
        raise Http404

    context = {
        "superset_report_url": dashboard_mapper[selected_dashboard_key],
    }
    return render(request, "dashboard.html", context)


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

