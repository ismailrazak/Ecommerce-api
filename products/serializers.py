from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from products.models import Product


class CustomerProductSerializer(ModelSerializer):

    class Meta:
        model = Product
        fields = ('id',"url",'name',"category", 'description', 'price', 'discount_percentage',"discounted_price", 'sold_by', 'stock', )

class SellerProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ('id',"url",'name',"category", 'description', 'price', 'discount_percentage',"discounted_price", 'sold_by', 'stock',"created_on","updated_on" )
        extra_kwargs = {
            'url': {'view_name': 'products-detail'}
        }

