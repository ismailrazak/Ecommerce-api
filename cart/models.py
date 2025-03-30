from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(
        "products.Product", related_name="all_carts", through="ProductQuantity"
    )

    def __str__(self):
        return f"{self.user}_cart"


class ProductQuantity(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="product_quantity"
    )
    product = models.ForeignKey("products.Product", models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_on = models.DateTimeField(auto_now=True)
    total_price = models.FloatField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"], name="unique_cart_product"
            )
        ]

    def save(self, *args, **kwargs):
        if not self.product.discounted_price:
            price = self.product.price
        price = self.product.discounted_price
        self.total_price = price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cart}_{self.product}"
