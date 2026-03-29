from django.db import models

class AuthorizedMember(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    npm = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    #potong nama jadi 2 kata
    def save(self, *args, **kwargs):
        words = self.full_name.strip().split()
        self.full_name = " ".join(words[:2])
        self.email = self.email.lower()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.email}"
    