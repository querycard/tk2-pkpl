from main.models import AuthorizedMember
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount


def get_user_email(user):
    if not user.is_authenticated:
        return ""

    # 1. Coba dari User.email
    email = (user.email or "").strip().lower()
    if email:
        return email

    # 2. Coba dari allauth EmailAddress
    email_address = EmailAddress.objects.filter(user=user).first()
    if email_address and email_address.email:
        return email_address.email.strip().lower()

    # 3. Coba dari SocialAccount.extra_data
    social_account = SocialAccount.objects.filter(user=user, provider="google").first()
    if social_account:
        extra_data = social_account.extra_data or {}
        email = (extra_data.get("email") or "").strip().lower()
        if email:
            return email

    return ""


def is_authorized_member(user):
    if not user.is_authenticated:
        return False

    email = get_user_email(user)
    if not email:
        return False

    return AuthorizedMember.objects.filter(
        email=email,
        is_active=True
    ).exists()