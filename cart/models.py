from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    products = models.ManyToManyField('products.Product',related_name='all_carts',through="ProductQuantity")

    def __str__(self):
        return f"{self.user}_cart"


class ProductQuantity(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='product_quantity')
    product= models.ForeignKey('products.Product',models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_on = models.DateTimeField(auto_now=True)
    bought_item = models.BooleanField(default=False)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cart','product'],name='unique_cart_product')
        ]