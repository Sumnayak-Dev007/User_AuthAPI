# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ("Extra", {"fields": ("phone_number", "date_of_birth", "last_login_ip")}),
    )

admin.site.register(CustomUser, CustomUserAdmin)