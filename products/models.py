import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.deconstruct import deconstructible


@deconstructible
class GenerateProfileImagePath:
    def __init__(self):
        pass

    def __call__(self, instance, filename):
        ext = filename.split(".")[-1]

        path = f"media/all_products/{instance.product.name}/images/"
        name = f"{filename}"
        return os.path.join(path, name)


image_path = GenerateProfileImagePath()


class Product(models.Model):
    id = models.UUIDField(
        primary_key=True, editable=False, unique=True, default=uuid.uuid4
    )
    name = models.CharField(max_length=400)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    discount_percentage = models.PositiveIntegerField(blank=True, null=True)
    discounted_price = models.DecimalField(
        blank=True, null=True, max_digits=10, decimal_places=2
    )
    sold_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="seller_products",
    )
    stock = models.PositiveIntegerField(default=1)
    ai_review = models.TextField(blank=True)

    class CategoryChoices(models.TextChoices):
        ELECTRONIC_DEVICES = ("ED", "Electronics Devices")
        HOME_APPLIANCES = ("HA", "Home Appliances")
        FASHION_ACCESSORIES = ("FA", "Fashion Accessories")
        SPORTS_EQUIPMENT = ("SE", "Sports Equipment")
        BOOKS_STATIONERY = ("BS", "Books & Stationery")
        BEAUTY_PRODUCTS = ("BP", "Beauty Products")
        TOYS_GAMES = ("TG", "Toys & Games")
        GROCERY_ITEMS = ("GI", "Grocery Items")
        FURNITURE_DECOR = ("FD", "Furniture & Decor")
        HEALTH_WELLNESS = ("HW", "Health & Wellness")

    category = models.CharField(max_length=2, choices=CategoryChoices)

    def save(self, *args, **kwargs):
        if self.discount_percentage:
            discount = (self.discount_percentage / 100) * (float(self.price))
            self.discounted_price = float(self.price) - discount
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products-detail", kwargs={"pk": self.pk})


def _max_product_images_validator(value):
    if ProductImage.objects.filter(product_id=value).count() >= 3:
        raise ValidationError("Max number of images are created for your product.")


class ProductImage(models.Model):
    image = models.ImageField(upload_to=image_path, null=True, blank=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_images",
        validators=(_max_product_images_validator,),
    )

    def __str__(self):
        return f"{self.product.name}_{self.id}"


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_reviews"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.reviewer}_{self.id}_review"


class Order(models.Model):
    id = models.UUIDField(
        primary_key=True, editable=False, unique=True, default=uuid.uuid4
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True
    )
    payment_id = models.CharField(max_length=20, blank=True)
    order_id = models.CharField(max_length=20, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    ordered_on = models.DateTimeField(auto_now_add=True)
    final_price = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-ordered_on"]
