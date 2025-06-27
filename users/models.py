from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)

    def __str__(self):
        return self.email

    def get_tokens(self):
        """Returns the tokens for the user."""
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
