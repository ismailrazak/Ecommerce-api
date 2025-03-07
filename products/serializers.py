from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from products.models import Product


class CustomerProductSerializer(ModelSerializer):

    class Meta:
        model = Product
        fields = ('id',"url",'name',"category", 'description', 'price', 'discount_percentage',"discounted_price", 'sold_by', 'stock', )

class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['image','product']


class SellerProductSerializer(ModelSerializer):
    images = ProductImageSerializer(many=True,required=False)
    class Meta:
        model = Product
        fields = ('id',"url",'name',"category", 'description', 'price', 'discount_percentage', 'stock',"created_on","updated_on",'images' )
        extra_kwargs = {
            'url': {'view_name': 'products-detail'}
        }

#todo add a product from api with images
