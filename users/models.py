from django.db import models
from django.contrib.auth.models import AbstractUser

class user(AbstractUser):
    email = models.EmailField(
        unique = True,
        verbose_name = 'Email Address'
    )

class profile(models.Model):
    user = models.OneToOneField(
        'users.user',
        on_delete = models.CASCADE,
        related_name = 'profile'
    )

    phone_number = models.CharField(
        max_length = 11,
        blank = True,
        null = True
    )

    avatar = models.ImageField(
        upload_to = 'profile_imags/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"