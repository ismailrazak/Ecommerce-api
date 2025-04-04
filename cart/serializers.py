from rest_framework import serializers

from cart.models import Cart, ProductQuantity
from products.serializers import CustomerProductSerializer


class ProductQuantitySerializer(serializers.ModelSerializer):
    product = serializers.HyperlinkedRelatedField(
        view_name="product-detail", read_only=True
    )

    class Meta:
        model = ProductQuantity
        fields = ["product", "quantity", "added_on", "total_price"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["category"] = instance.product.get_category_display()
        return data


class CartSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "product"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["user"] = instance.user.username
        return data

    def get_product(self, obj):
        cart_items = obj.product_quantity.all()
        return ProductQuantitySerializer(
            cart_items, many=True, context={"request": self.context["request"]}
        ).data


# todo replace serializermethod with product quantity serializer
