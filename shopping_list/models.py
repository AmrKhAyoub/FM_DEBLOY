from django.db import models
from django.contrib.auth.models import User

class ShoppingListItem(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50, blank=True)
    purchased = models.BooleanField(default=False)

    def __str__(self):
        return self.item_name