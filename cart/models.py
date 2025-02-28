from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    products = models.ManyToManyField('products.Product',related_name='cart_products')

    def __str__(self):
        return f"{self.user}_cart"
