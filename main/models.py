from django.db import models
from django.contrib.auth.models import User

class AuthorizedMember(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    npm = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        words = self.full_name.strip().split()
        self.full_name = " ".join(words[:2])
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.email}"


class ThemePreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    primary_color = models.CharField(max_length=20, default='#3B5BDB')
    text_color = models.CharField(max_length=20, default='#111111')
    font_family = models.CharField(max_length=50, default='Inter')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Theme for {self.user.email}"


class AuditLog(models.Model):
    actor_email = models.CharField(max_length=100)
    action = models.CharField(max_length=50)
    target = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.actor_email} - {self.action} - {self.status}"