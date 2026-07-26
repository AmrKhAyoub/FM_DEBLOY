from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # we can add any additional fields in future if needed
    def __str__(self):
        return self.username
