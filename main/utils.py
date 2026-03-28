from main.models import AuthorizedMember

def is_authorized_member(user):
    if not user.is_authenticated:
        return False

    return AuthorizedMember.objects.filter(
        email=user.email.lower(),
        is_active=True
    ).exists()