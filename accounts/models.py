import os
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import F
from django.utils.deconstruct import deconstructible

from products.models import Product


@deconstructible
class GenerateProfileImagePath:
    """
    Generates a proper file path to store the profile photo of a user.
    """
    def __init__(self):
        pass

    def __call__(self, instance, filename):
        ext = filename.split(".")[-1]

        path = f"media/profiles/images/{instance.username}_{instance.id}"
        name = f"main.{ext}"
        return os.path.join(path, name)
image_path =GenerateProfileImagePath()

class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True, editable=False, unique=True, default=uuid.uuid4
    )
    address = models.CharField(max_length=400)
    profile_photo = models.ImageField(upload_to=image_path,null=True,blank=True)

    def delete(self, using=None, keep_parents=False):
        products = []
        if self.groups.filter(name='customers').exists():
            for product_quantity in self.cart.product_quantity.all():
                quantity=product_quantity.quantity
                product=product_quantity.product
                products.append(product)
                product.stock=F('stock')+quantity
            Product.objects.bulk_update(products,['stock'])
        super().delete()
