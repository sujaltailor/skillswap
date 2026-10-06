from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout

from .models import Skill, Profile, ExchangeRequest


# =========================================================
# USER HOME / PROFILE
# =========================================================

@login_required(login_url="login")
def home(request):

    skills = Skill.objects.all()

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        request.user.first_name = request.POST.get("name")
        request.user.save()

        profile.bio = request.POST.get("bio")

        profile.skills_to_teach.set(
            request.POST.getlist("teach_skills")
        )

        profile.skills_to_learn.set(
            request.POST.getlist("learn_skills")
        )

        profile.save()

        return redirect("dashboard")

    return render(
        request,
        "home.html",
        {
            "skills": skills,
            "profile": profile
        }
    )


# =========================================================
# USER REGISTER
# =========================================================

def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "register.html",
                {
                    "error":
                    "Username already exists!"
                }
            )

        user = User.objects.create_user(
            username=username,
            password=password
        )

        user.save()

        return redirect("login")

    return render(
        request,
        "register.html"
    )


# =========================================================
# USER LOGIN
# =========================================================

def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            auth_login(
                request,
                user
            )

            return redirect("dashboard")

        return render(
            request,
            "login.html",
            {
                "error":
                "Invalid username or password!"
            }
        )

    return render(
        request,
        "login.html"
    )


# =========================================================
# USER LOGOUT
# =========================================================

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

    request_count = ExchangeRequest.objects.filter(
        receiver=profile,
        status="Pending"
    ).count()

    query = request.GET.get(
        "q",
        ""
    ).strip()

    profiles = Profile.objects.none()

    if query:

        profiles = Profile.objects.filter(
            skills_to_teach__name__icontains=query
        ).exclude(
            user=request.user
        ).select_related(
            "user"
        ).distinct()

    return render(
        request,
        "dashboard.html",
        {
            "profile": profile,
            "query": query,
            "profiles": profiles,
            "request_count": request_count
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
        ).exclude(
            user=request.user
        ).select_related(
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

    receiver = get_object_or_404(
        Profile,
        id=profile_id
    )

    sender = get_object_or_404(
        Profile,
        user=request.user
    )

    # User cannot send request to himself
    if sender == receiver:

        return redirect("dashboard")

    # Check pending request already exists
    existing_request = ExchangeRequest.objects.filter(
        sender=sender,
        receiver=receiver,
        status="Pending"
    ).exists()

    if existing_request:

        return redirect("dashboard")

    if request.method == "POST":

        message = request.POST.get(
            "message",
            ""
        )

        ExchangeRequest.objects.create(
            sender=sender,
            receiver=receiver,
            message=message
        )

        return redirect("requests")

    return render(
        request,
        "send_request.html",
        {
            "receiver": receiver
        }
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

@login_required(login_url="login")
def accept_request(request, request_id):

    exchange_request = get_object_or_404(
        ExchangeRequest,
        id=request_id
    )

    # Only receiver can accept
    if exchange_request.receiver.user != request.user:

        return redirect("requests")

    exchange_request.status = "Accepted"

    exchange_request.save()

    return redirect("requests")


# =========================================================
# REJECT REQUEST
# =========================================================

@login_required(login_url="login")
def reject_request(request, request_id):

    exchange_request = get_object_or_404(
        ExchangeRequest,
        id=request_id
    )

    # Only receiver can reject
    if exchange_request.receiver.user != request.user:

        return redirect("requests")

    exchange_request.status = "Rejected"

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

@user_passes_test(
    is_admin,
    login_url="login"
)
def create_user(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        first_name = request.POST.get(
            "first_name",
            ""
        ).strip()

        last_name = request.POST.get(
            "last_name",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        # Username already exists
        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "create_user.html",
                {
                    "error":
                    "Username already exists!"
                }
            )

        # Password validation
        if len(password) < 6:

            return render(
                request,
                "create_user.html",
                {
                    "error":
                    "Password must be at least 6 characters!"
                }
            )

        # Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Create profile
        Profile.objects.get_or_create(
            user=user
        )

        return redirect(
            "admin_dashboard"
        )

    return render(
        request,
        "create_user.html"
    )


# =========================================================
# ADMIN DELETE USER
# =========================================================

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

@user_passes_test(
    is_admin,
    login_url="login"
)
def edit_user(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id
    )

    # Admin / superuser ko edit nahi karna
    if user.is_staff or user.is_superuser:
        return redirect("admin_dashboard")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        first_name = request.POST.get(
            "first_name",
            ""
        ).strip()

        last_name = request.POST.get(
            "last_name",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        # Check username already exists
        if User.objects.filter(
            username=username
        ).exclude(
            id=user.id
        ).exists():

            return render(
                request,
                "edit_user.html",
                {
                    "user": user,
                    "error":
                    "Username already exists!"
                }
            )

        # Update user information
        user.username = username
        user.first_name = first_name
        user.last_name = last_name

        # Password only update if entered
        if password:

            if len(password) < 6:

                return render(
                    request,
                    "edit_user.html",
                    {
                        "user": user,
                        "error":
                        "Password must be at least 6 characters!"
                    }
                )

            user.set_password(password)

        user.save()

        return redirect(
            "admin_dashboard"
        )

    return render(
        request,
        "edit_user.html",
        {
            "user": user
        }
    )