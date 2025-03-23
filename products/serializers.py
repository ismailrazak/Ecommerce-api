from decouple import config
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from products.models import Product, ProductImage,Review
import redis
from celery.result import AsyncResult
from products.tasks import ai_summary_review_task

r = redis.Redis(
    host=config("REDIS_HOST", default="redis"),
    port=config("REDIS_PORT", default=6379),
    db=0,
    decode_responses=True,
)

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id','reviewer','description']

    def to_representation(self, instance):
        data  = super().to_representation(instance)
        data['reviewer']= instance.reviewer.username
        return data

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['url','image']
        extra_kwargs = {
            'url': {'view_name': 'product_image_detail'}
        }

class CustomerProductSerializer(ModelSerializer):
    images = ProductImageSerializer(many=True,source='product_images',read_only=True)
    reviews = ReviewSerializer(many=True,read_only=True,source='product_reviews')
    write_review= serializers.CharField(allow_blank=True,allow_null=True,write_only=True)
    class Meta:
        model = Product
        fields = ('id',"url",'name',"category", 'description', 'price', 'discount_percentage',"discounted_price", 'sold_by', 'stock','images','reviews','write_review','ai_review' )
        read_only_fields=['name','category','description','price', 'discount_percentage',"discounted_price", 'sold_by', 'stock','ai_review']

    def update(self,instance, validated_data):
        written_review=validated_data.pop('write_review')
        if instance.product_reviews.filter(reviewer=self.context['request'].user).exists():
            raise serializers.ValidationError({'error':'You have already made a review for this product.'})
        Review.objects.create(description=written_review,reviewer=self.context['request'].user,product=instance)
        reviews_counter=r.incr(f"total_reviews_{instance.id}")
        if reviews_counter == 5:
            product_id=instance.id
            ai_summary_review_task.delay(product_id)
            r.set(f"total_reviews_{instance.id}",0)
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['category']=instance.get_category_display()
        data['sold_by']=instance.sold_by.username
        return data

class SellerProductSerializer(ModelSerializer):
    images = ProductImageSerializer(many=True,source='product_images',read_only=True)
    uploaded_images = serializers.ListField(child=serializers.ImageField(allow_empty_file=False,use_url=False),write_only=True)

    class Meta:
        model = Product
        fields = ('id',"url",'name',"category", 'description', 'price', 'discount_percentage', 'stock',"created_on","updated_on",'images','uploaded_images' )
        extra_kwargs = {
            'url': {'view_name': 'products-detail'}
        }

    def create(self, validated_data):
        uploaded_images=validated_data.pop('uploaded_images')
        product = Product.objects.create(**validated_data)
        ProductImage.objects.bulk_create([ProductImage(image=image,product=product)for image in uploaded_images])
        return product

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['category']=instance.get_category_display()
        return data


















