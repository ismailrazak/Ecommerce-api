from rest_framework import serializers

from cart.models import Cart, ProductQuantity


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
    product = ProductQuantitySerializer(
        many=True, read_only=True, source="product_quantity"
    )

    class Meta:
        model = Cart
        fields = ["id", "user", "product"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["user"] = instance.user.username
        return data
