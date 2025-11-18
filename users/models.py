# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

india_phone_validator = RegexValidator(
    regex=r'^(?:\+91|91)?[6-9]\d{9}$',
    message="Enter a valid Indian phone number (10 digits starting with 6-9, optional +91 or 91 prefix)."
)

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, validators=[india_phone_validator])
    date_of_birth = models.DateField(null=True, blank=True)
    last_login_ip = models.CharField(max_length=45, null=True, blank=True)

    def __str__(self):
        return self.username or self.email