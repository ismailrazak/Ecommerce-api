from rest_framework import serializers

from cart.models import Cart, ProductQuantity
from products.serializers import CustomerProductSerializer

class ProductQuantitySerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductQuantity
        fields = ['product','quantity','added_on','total_price']


class CartSerializer(serializers.ModelSerializer):
    product =  serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id','user','product']



    def get_product(self,obj):
        cart_items = obj.product_quantity.filter(bought_item=False)
        return ProductQuantitySerializer(cart_items,many=True).data


#todo make url for product in cart? usign get_absolute_url

#add payment integration