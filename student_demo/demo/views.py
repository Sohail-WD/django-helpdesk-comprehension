from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.urls import reverse

from .company import load_company_config
from .forms import RoleLoginForm

from django.contrib import messages
from django.views.decorators.http import require_POST


def home(request):
    return render(
        request,
        "demo/home.html",
        {"demo": load_company_config()},
    )


def _role_login(
    request,
    *,
    role,
    destination_name,
    require_staff=False,
):
    if request.user.is_authenticated and request.method == "GET":
        logout(request)

    form = RoleLoginForm(request.POST or None)
    error_message = None

    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )

        if user is None:
            error_message = "Username or password is incorrect."

        elif require_staff and not user.is_staff:
            error_message = "This account is not a support-agent account."

        elif not require_staff and user.is_staff:
            error_message = (
                "Use the support-agent or manager entry point for this account."
            )

        else:
            login(request, user)
            return redirect(destination_name)

    return render(
        request,
        "demo/role_login.html",
        {
            "form": form,
            "role": role,
            "error_message": error_message,
            "demo": load_company_config(),
        },
    )



def customer_entry(request):
    return _role_login(
        request,
        role="Customer",
        destination_name="helpdesk:my-tickets",
        require_staff=False,
    )


def agent_entry(request):
    return _role_login(
        request,
        role="Support agent",
        destination_name="helpdesk:dashboard",
        require_staff=True,
    )


def manager_entry(request):
    if request.user.is_authenticated:
        logout(request)

    return redirect(reverse("admin:login"))

@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("demo-home")

