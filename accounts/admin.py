from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import User
# Register your models here.

class CustomModelAdmin(ModelAdmin):
    readonly_fields = ['password']

admin.site.register(User,CustomModelAdmin)