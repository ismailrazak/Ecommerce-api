from dj_rest_auth.registration.serializers import RegisterSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

from cart.models import Cart
from cart.serializers import ProductQuantitySerializer
from products.models import Product
from products.serializers import OrderSerializer


class SellerProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["name", "price"]


class CustomerAccountDetailSerializer(serializers.ModelSerializer):
    orders = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "address",
            "profile_photo",
            "email",
            "orders",
        ]

    def get_orders(self, obj):
        orders = obj.orders.exclude(payment_id="")
        return OrderSerializer(
            orders, context={"request": self.context["request"]}, many=True
        ).data


class SellerAccountDetailSerializer(serializers.ModelSerializer):
    products = SellerProductsSerializer(
        read_only=True, many=True, source="seller_products"
    )

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "address",
            "profile_photo",
            "email",
            "products",
        ]


class UserRegistrationSerializer(RegisterSerializer):
    """Using Custom Register serializer  to add address and profile_photo attributes.
    also overwrite adapter for saving.
    """

    address = serializers.CharField()
    profile_photo = serializers.ImageField(required=False)

    def get_cleaned_data(self):
        data_dict = super().get_cleaned_data()
        data_dict["address"] = self.validated_data.get("address", "")
        data_dict["profile_photo"] = self.validated_data.get("profile_photo")
        return data_dict
