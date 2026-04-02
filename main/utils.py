from main.models import AuthorizedMember
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount


def get_user_email(user):
    if not user.is_authenticated:
        return ""

    # 1. Dari User.email
    email = (user.email or "").strip().lower()
    if email:
        return email

    # 2. Dari allauth EmailAddress
    email_address = EmailAddress.objects.filter(user=user).first()
    if email_address and email_address.email:
        return email_address.email.strip().lower()

    # 3. Dari SocialAccount.extra_data
    social_account = SocialAccount.objects.filter(user=user, provider="google").first()
    if social_account:
        extra_data = social_account.extra_data or {}

        # beberapa kemungkinan key email
        possible_emails = [
            extra_data.get("email"),
            extra_data.get("emailAddress"),
        ]

        for e in possible_emails:
            e = (e or "").strip().lower()
            if e:
                return e

    return ""


def is_authorized_member(user):
    if not user.is_authenticated:
        return False

    email = get_user_email(user)
    if not email:
        return False

    return AuthorizedMember.objects.filter(
        email__iexact=email,
        is_active=True
    ).exists()