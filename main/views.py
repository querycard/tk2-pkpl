from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .utils import is_authorized_member, get_user_email
from .models import AuthorizedMember, ThemePreference, AuditLog
import json

VALID_COLORS = [
    '#3B5BDB',  # Biru
    '#7c3aed',  # Ungu
    '#d14fd1',  # Pink
    '#dc8748',  # Jingga
    '#dfca56',  # Kuning
    '#db4d45',  # Merah
    '#111111',  # Hitam
    '#374151',  # Abu Gelap
    '#4f46e5',  # Nila
    '#ffffff',  # Putih
    '#2563eb',  # Biru
    '#16a34a',  # Hijau
    '#ef4444',  # Merah
]

VALID_FONTS = ['Inter', 'Poppins']


def get_user_theme(user):
    if not user.is_authenticated:
        return ThemePreference(
            primary_color='#3B5BDB',
            text_color='#111111',
            font_family='Inter'
        )

    # 1. Coba ambil berdasarkan user sekarang
    try:
        return ThemePreference.objects.get(user=user)
    except ThemePreference.DoesNotExist:
        pass

    # 2. Fallback: cari theme milik akun lain dengan email yang sama
    #    Ini buat jaga-jaga kalau record User berubah tapi email sama
    fallback_theme = ThemePreference.objects.filter(
        user__email__iexact=user.email
    ).first()

    if fallback_theme:
        fallback_theme.user = user
        fallback_theme.save()
        return fallback_theme

    # 3. Kalau belum ada sama sekali, buat baru
    return ThemePreference.objects.create(
        user=user,
        primary_color='#3B5BDB',
        text_color='#111111',
        font_family='Inter'
    )


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
        ('#3B5BDB', 'Biru'),
        ('#7c3aed', 'Ungu'),
        ('#d14fd1', 'Pink'),
        ('#dc8748', 'Jingga'),
        ('#dfca56', 'Kuning'),
        ('#db4d45', 'Merah'),
    ]

    font_colors = [
        ('#111111', 'Hitam'),
        ('#374151', 'Abu Gelap'),
        ('#4f46e5', 'Nila'),
        ('#7c3aed', 'Ungu'),
        ('#ffffff', 'Putih'),
        ('#2563eb', 'Biru'),
        ('#16a34a', 'Hijau'),
        ('#ef4444', 'Merah'),
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
        AuditLog.objects.create(
            actor_email=email,
            action="theme_update",
            status="forbidden"
        )
        return JsonResponse({"error": "Forbidden"}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    primary_color = data.get('primary_color')
    text_color = data.get('text_color')
    font_family = data.get('font_family', 'Inter')

    if primary_color not in VALID_COLORS or text_color not in VALID_COLORS:
        return JsonResponse({"error": "Invalid color"}, status=400)

    if font_family not in VALID_FONTS:
        return JsonResponse({"error": "Invalid font"}, status=400)

    theme = get_user_theme(request.user)
    theme.primary_color = primary_color
    theme.text_color = text_color
    theme.font_family = font_family
    theme.save()

    AuditLog.objects.create(
        actor_email=get_user_email(request.user),
        action="theme_update",
        status="success",
        notes=f"bg={primary_color}, text={text_color}, font={font_family}"
    )

    return JsonResponse({"success": True})