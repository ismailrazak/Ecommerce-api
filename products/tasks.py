import redis
from celery import shared_task
from decouple import config
from django.core.cache import cache
from google import genai

from products.models import Product
from products.serializers import CustomerProductSerializer

client = genai.Client(api_key=config("API_KEY"))
r = redis.Redis(
    host=config("REDIS_HOST", default="redis"),
    port=config("REDIS_PORT", default=6379),
    db=0,
    decode_responses=True,
)


@shared_task(autoretry_for=(Exception,), max_retries=1, queue="ai_summary_queue")
def ai_summary_review_task(product_id):
    counter = 1
    all_descriptions = ""
    product = Product.objects.filter(id=product_id).first()
    reviews = product.product_reviews.all()[:5]
    for review in reviews:
        all_descriptions += f"Review {counter} : {review.description}"
        counter += 1
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"""
        Your job is to summarize reviews for a product based on the reviews given to you in a formal and simple to understand way.
        summarize those reviews into 5 lines while maintaining a proper balance between the pros and cons of the product.
        you will given a list of reviews and when possible a ai summary review. analyze both of these and generate a honest non-biased review while maintaing factual accuracy.
        Ai Review:{product.ai_review}
        list of reviews:{all_descriptions}
        
        Example:
        Customers appreciate the phone's camera quality, speed, and display. They find the main camera quality superb in day light, with good charging speed. The high refresh rate makes the animations very smooth. The apps open instantly and the higher refresh rate makes the animation smoother. The phone looks classy and has a premium design. The battery life is long-lasting, and the AI feature is also very good. Overall, customers are satisfied with the performance, display quality, battery life, and overall functionality of the phone.
        """,
    )
    product.ai_review = response.text
    product.save()


@shared_task
def hot_deals_task():
    categories = list(Product.CategoryChoices)
    for category in categories:
        products = Product.objects.filter(category=category.value).order_by(
            "-discount_percentage"
        )[:50]
        serialized_data = HotDealsTaskSerializer(products, many=True)
        cache_key = f"category:{category.value}"
        cache.set(cache_key, serialized_data.data, 3600)


class HotDealsTaskSerializer(CustomerProductSerializer):
    class Meta(CustomerProductSerializer.Meta):
        fields = (
            "id",
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
