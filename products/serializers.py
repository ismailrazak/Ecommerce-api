from decouple import config
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from products.models import Order, Product, ProductImage, Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "url", "reviewer", "description"]
        extra_kwargs = {"url": {"view_name": "product_review"}}
        read_only_fields = [
            "reviewer",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["reviewer"] = instance.reviewer.username
        return data


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["url", "image"]
        extra_kwargs = {"url": {"view_name": "product_image_detail"}}


class CustomerProductSerializer(ModelSerializer):
    images = ProductImageSerializer(many=True, source="product_images", read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True, source="product_reviews")

    class Meta:
        model = Product
        fields = (
            "id",
            "url",
            "name",
            "category",
            "description",
            "price",
            "discount_percentage",
            "discounted_price",
            "sold_by",
            "stock",
            "images",
            "reviews",
            "ai_review",
        )
        read_only_fields = [
            "name",
            "category",
            "description",
            "price",
            "discount_percentage",
            "discounted_price",
            "sold_by",
            "stock",
            "ai_review",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["category"] = instance.get_category_display()
        data["sold_by"] = instance.sold_by.username
        return data


class SellerProductSerializer(ModelSerializer):
    images = ProductImageSerializer(many=True, source="product_images", read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "url",
            "name",
            "category",
            "description",
            "price",
            "discount_percentage",
            "discounted_price",
            "stock",
            "created_on",
            "updated_on",
            "images",
            "uploaded_images",
        )
        extra_kwargs = {"url": {"view_name": "products-detail"}}
        read_only_fields = ["discounted_price"]

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images")
        product = Product.objects.create(**validated_data)
        ProductImage.objects.bulk_create(
            [ProductImage(image=image, product=product) for image in uploaded_images]
        )
        return product

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["category"] = instance.get_category_display()
        return data


class OrderSerializer(serializers.ModelSerializer):
    product = serializers.HyperlinkedRelatedField(
        view_name="product-detail", read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "product",
            "order_id",
            "payment_id",
            "quantity",
            "final_price",
            "ordered_on",
        ]
        read_only_fields = [
            "order_id",
            "payment_id",
            "quantity",
            "final_price",
            "ordered_on",
        ]
