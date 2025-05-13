from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_librarian = models.BooleanField(default=False)
    is_standard_user = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    student_id = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username