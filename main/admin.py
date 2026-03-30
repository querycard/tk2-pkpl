from django.contrib import admin
from .models import AuthorizedMember

# Mendaftarkan tabel AuthorizedMember ke panel Admin
admin.site.register(AuthorizedMember)