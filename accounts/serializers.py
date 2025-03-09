from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from cart.models import Cart
from cart.serializers import ProductQuantitySerializer
from products.models import Product
from django.contrib.auth.models import Group




class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password1 = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id','username','first_name','last_name', 'address', 'profile_photo', "email", "password", "password1"]

    def validate(self, data):
        password = data.get("password")
        password1 = data.get("password1")
        if password != password1:
            raise serializers.ValidationError({"error": "passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("password")
        password1 = validated_data.pop("password1")
        user = get_user_model().objects.create(**validated_data)
        user.set_password(password1)
        user.save()
        return user



class SellerRegistrationSerializer(UserRegistrationSerializer):

    def create(self, validated_data):

        user=super().create(validated_data)
        seller_group = Group.objects.get(name='sellers')
        user.groups.add(seller_group)
        return user

class CustomerRegistrationSerializer(UserRegistrationSerializer):

    def create(self, validated_data):


        user = super().create(validated_data)
        customer_group = Group.objects.get(name='customers')
        user.groups.add(customer_group)
        Cart.objects.create(user=user)
        return user

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model =Product
        fields = ['name','price']

class CustomerAccountDetailSerializer(serializers.ModelSerializer):
    orders = serializers.SerializerMethodField()
    # here orders name is  same as related_name 'orders' of product model . Thats why it works
    class Meta:
        model = get_user_model()
        fields  =['id','username','first_name','last_name', 'address', 'profile_photo', "email",'orders']

    def get_orders(self,obj):
        cart= obj.cart
        products_ordered = cart.product_quantity.filter(bought_item=True)
        return ProductQuantitySerializer(products_ordered,many=True).data

class SellerAccountDetailSerializer(serializers.ModelSerializer):
    products = OrderSerializer(read_only=True, many=True,source='seller_products')
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name', 'address', 'profile_photo', "email", 'products']



