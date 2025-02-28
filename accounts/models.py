import os
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.deconstruct import deconstructible


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



