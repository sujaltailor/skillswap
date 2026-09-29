from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.views.decorators.http import require_POST

from .models import Skill, Profile, ExchangeRequest
from .forms import (
    AdminUserCreationForm,
    AdminUserUpdateForm,
    ExchangeRequestForm,
    LoginForm,
    ProfileForm,
    RegistrationForm,
)


# =========================================================
# USER HOME / PROFILE
# =========================================================

@login_required(login_url="login")
def home(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("dashboard")

    return render(request, "home.html", {"form": form, "profile": profile})

# =========================================================
# USER REGISTER
# =========================================================

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        Profile.objects.create(user=user)
        return redirect("login")

    return render(request, "register.html", {"form": form})

# =========================================================
# USER LOGIN
# =========================================================

def user_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        auth_login(request, form.get_user())
        return redirect(request.GET.get("next") or "dashboard")

    return render(request, "login.html", {"form": form})

# =========================================================
# USER LOGOUT
# =========================================================

@require_POST
@login_required(login_url="login")
def logout_user(request):

    logout(request)

    return redirect("login")


# =========================================================
# USER DASHBOARD
# =========================================================

@login_required(login_url="login")
def dashboard(request):

    profile = Profile.objects.filter(
        user=request.user
    ).first()

    if not profile:
        return redirect("home")

    query = request.GET.get(
        "q",
        ""
    ).strip()

    profiles = Profile.objects.none()

    if query:

        profiles = Profile.objects.filter(
            skills_to_teach__name__icontains=query
        ).exclude(user=request.user).select_related(
            "user"
        ).distinct()

    return render(
        request,
        "dashboard.html",
        {
            "profile": profile,
            "query": query,
            "profiles": profiles
        }
    )


# =========================================================
# FIND SKILLS
# =========================================================

@login_required(login_url="login")
def find_skills(request):

    query = request.GET.get(
        "q",
        ""
    ).strip()

    profiles = Profile.objects.none()

    if query:

        profiles = Profile.objects.filter(
            skills_to_teach__name__icontains=query
        ).exclude(user=request.user).select_related(
            "user"
        ).distinct()

    return render(
        request,
        "find_skills.html",
        {
            "query": query,
            "profiles": profiles
        }
    )


# =========================================================
# SEND EXCHANGE REQUEST
# =========================================================

@login_required(login_url="login")
def send_request(request, profile_id):
    receiver = get_object_or_404(Profile, id=profile_id)
    sender = get_object_or_404(Profile, user=request.user)

    if sender == receiver:
        return redirect("dashboard")

    if ExchangeRequest.objects.filter(
        sender=sender,
        receiver=receiver,
        status=ExchangeRequest.Status.PENDING,
    ).exists():
        return redirect("dashboard")

    form = ExchangeRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ExchangeRequest.objects.get_or_create(
            sender=sender,
            receiver=receiver,
            status=ExchangeRequest.Status.PENDING,
            defaults={"message": form.cleaned_data["message"]},
        )
        return redirect("requests")

    return render(
        request,
        "send_request.html",
        {"receiver": receiver, "form": form},
    )

# =========================================================
# REQUESTS PAGE
# =========================================================

@login_required(login_url="login")
def requests_page(request):

    profile = get_object_or_404(
        Profile,
        user=request.user
    )

    # Requests sent by current user
    sent_requests = ExchangeRequest.objects.filter(
        sender=profile
    ).select_related(
        "receiver__user"
    ).order_by(
        "-created_at"
    )

    # Requests received by current user
    received_requests = ExchangeRequest.objects.filter(
        receiver=profile
    ).select_related(
        "sender__user"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "requests.html",
        {
            "sent_requests": sent_requests,
            "received_requests": received_requests
        }
    )


# =========================================================
# ACCEPT REQUEST
# =========================================================

@require_POST
@login_required(login_url="login")
def accept_request(request, request_id):

    exchange_request = get_object_or_404(
        ExchangeRequest,
        id=request_id
    )

    # Only receiver can accept
    if exchange_request.receiver.user != request.user:

        return redirect("requests")

    exchange_request.status = ExchangeRequest.Status.ACCEPTED

    exchange_request.save()

    return redirect("requests")


# =========================================================
# REJECT REQUEST
# =========================================================

@require_POST
@login_required(login_url="login")
def reject_request(request, request_id):

    exchange_request = get_object_or_404(
        ExchangeRequest,
        id=request_id
    )

    # Only receiver can reject
    if exchange_request.receiver.user != request.user:

        return redirect("requests")

    exchange_request.status = ExchangeRequest.Status.REJECTED

    exchange_request.save()

    return redirect("requests")


# =========================================================
# ADMIN CHECK
# =========================================================

def is_admin(user):

    return user.is_authenticated and (
        user.is_staff or user.is_superuser
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

def admin_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        # Only staff or superuser can login as admin
        if user is not None and (
            user.is_staff or user.is_superuser
        ):

            auth_login(
                request,
                user
            )

            return redirect(
                "admin_dashboard"
            )

        return render(
            request,
            "admin_login.html",
            {
                "admin_error":
                "Invalid admin username or password!"
            }
        )

    return render(
        request,
        "admin_login.html"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@user_passes_test(
    is_admin,
    login_url="login"
)
def admin_dashboard(request):

    # Only normal users
    users = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).order_by(
        "-date_joined"
    )

    total_users = users.count()

    return render(
        request,
        "admin_dashboard.html",
        {
            "total_users": total_users,
            "users": users
        }
    )


# =========================================================
# ADMIN CREATE USER
# =========================================================

@user_passes_test(is_admin, login_url="login")
def create_user(request):
    form = AdminUserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        Profile.objects.get_or_create(user=user)
        return redirect("admin_dashboard")

    return render(request, "create_user.html", {"form": form})

# =========================================================
# ADMIN DELETE USER
# =========================================================

@require_POST
@user_passes_test(
    is_admin,
    login_url="login"
)
def delete_user(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id
    )

    # Admin/superuser cannot be deleted
    if user.is_staff or user.is_superuser:

        return redirect(
            "admin_dashboard"
        )

    user.delete()

    return redirect(
        "admin_dashboard"
    )

# =========================================================
# ADMIN EDIT USER
# =========================================================

@user_passes_test(is_admin, login_url="login")
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_staff or user.is_superuser:
        return redirect("admin_dashboard")

    form = AdminUserUpdateForm(request.POST or None, instance=user)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("admin_dashboard")

    return render(request, "edit_user.html", {"form": form, "user": user})
