from django.urls import path
from . import views


urlpatterns = [

    # =========================
    # USER
    # =========================

    path(
        "home/",
        views.home,
        name="home"
    ),

    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "login/",
        views.user_login,
        name="login"
    ),

    path(
        "logout/",
        views.logout_user,
        name="logout"
    ),


    # =========================
    # USER DASHBOARD
    # =========================

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),


    # =========================
    # SEARCH
    # =========================

    path(
        "find-skills/",
        views.find_skills,
        name="find_skills"
    ),


    # =========================
    # EXCHANGE REQUEST
    # =========================

    path(
        "send-request/<int:profile_id>/",
        views.send_request,
        name="send_request"
    ),

    path(
        "requests/",
        views.requests_page,
        name="requests"
    ),

    path(
        "request/<int:request_id>/accept/",
        views.accept_request,
        name="accept_request"
    ),

    path(
        "request/<int:request_id>/reject/",
        views.reject_request,
        name="reject_request"
    ),


    # =========================
    # CUSTOM ADMIN
    # =========================

    path(
        "admin-login/",
        views.admin_login,
        name="admin_login"
    ),

    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),

    path(
        "admin-users/create/",
        views.create_user,
        name="create_user"
    ),

    path(
        "admin-users/edit/<int:user_id>/",
        views.edit_user,
        name="edit_user"
    ),

    path(
        "admin-users/delete/<int:user_id>/",
        views.delete_user,
        name="delete_user"
    ),

]