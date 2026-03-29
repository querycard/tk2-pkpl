from django.shortcuts import render, redirect
from .utils import is_authorized_member, get_user_email
from .models import AuthorizedMember


def home_view(request):
    role = "guest"

    if request.user.is_authenticated:
        if is_authorized_member(request.user):
            role = "member"
        else:
            role = "viewer"

    members = AuthorizedMember.objects.filter(is_active=True).order_by('full_name')

    return render(request, "main/home.html", {
        "role": role,
        "members": members,
    })


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("home")

    if not is_authorized_member(request.user):
        return redirect("home")

    return render(request, "main/dashboard.html", {"role": "member"})