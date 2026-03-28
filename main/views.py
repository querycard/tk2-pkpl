from django.shortcuts import render, redirect
from .utils import is_authorized_member

def home_view(request):
    return render(request, "main/home.html")

def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("home")

    if not is_authorized_member(request.user):
        return redirect("home")

    return render(request, "main/dashboard.html")