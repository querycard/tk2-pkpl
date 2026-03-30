from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .utils import is_authorized_member, get_user_email
from .models import AuthorizedMember, ThemePreference, AuditLog
import json

VALID_COLORS = ['#ef4444','#f97316','#ca8a04','#16a34a','#2563eb','#4f46e5','#9333ea','#111111','#ffffff','#3B5BDB']
VALID_FONTS  = ['Inter', 'Georgia', 'Courier New', 'Arial']

def get_user_theme(user):
    if user.is_authenticated:
        theme, _ = ThemePreference.objects.get_or_create(user=user)
        return theme
    return ThemePreference(primary_color='#3B5BDB', text_color='#111111', font_family='Inter')

def home_view(request):
    role = "guest"
    if request.user.is_authenticated:
        role = "member" if is_authorized_member(request.user) else "viewer"

    members = AuthorizedMember.objects.filter(is_active=True).order_by('full_name')
    theme = get_user_theme(request.user)

    return render(request, "main/home.html", {
        "role": role,
        "members": members,
        "theme": theme,
    })

def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("home")
    if not is_authorized_member(request.user):
        AuditLog.objects.create(
            actor_email=get_user_email(request.user),
            action="dashboard_access",
            status="forbidden"
        )
        return redirect("home")

    AuditLog.objects.create(
        actor_email=get_user_email(request.user),
        action="dashboard_access",
        status="success"
    )

    theme = get_user_theme(request.user)
    bg_colors = [
        ('#ef4444','Merah'),
        ('#f97316','Jingga'),
        ('#ca8a04','Kuning'),
        ('#16a34a','Hijau'),
        ('#2563eb','Biru'),
        ('#4f46e5','Nila'),
        ('#9333ea','Ungu'),
        ('#ffffff','Putih'),
    ]
    font_colors = [
        ('#ef4444','Merah'),
        ('#f97316','Jingga'),
        ('#ca8a04','Kuning'),
        ('#16a34a','Hijau'),
        ('#2563eb','Biru'),
        ('#4f46e5','Nila'),
        ('#9333ea','Ungu'),
        ('#111111','Hitam'),
    ]
    return render(request, "main/dashboard.html", {
        "role": "member",
        "theme": theme,
        "bg_colors": bg_colors,
        "font_colors": font_colors,
    })

@require_POST
def update_theme_view(request):
    if not request.user.is_authenticated or not is_authorized_member(request.user):
        email = get_user_email(request.user) if request.user.is_authenticated else "guest"
        AuditLog.objects.create(actor_email=email, action="theme_update", status="forbidden")
        return JsonResponse({"error": "Forbidden"}, status=403)

    data = json.loads(request.body)
    primary_color = data.get('primary_color')
    text_color    = data.get('text_color')
    font_family   = data.get('font_family', 'Inter')

    if primary_color not in VALID_COLORS or text_color not in VALID_COLORS:
        return JsonResponse({"error": "Invalid color"}, status=400)
    if font_family not in VALID_FONTS:
        return JsonResponse({"error": "Invalid font"}, status=400)

    theme = get_user_theme(request.user)
    theme.primary_color = primary_color
    theme.text_color    = text_color
    theme.font_family   = font_family
    theme.save()

    AuditLog.objects.create(
        actor_email=get_user_email(request.user),
        action="theme_update",
        status="success",
        notes=f"bg={primary_color}, text={text_color}, font={font_family}"
    )

    return JsonResponse({"success": True})