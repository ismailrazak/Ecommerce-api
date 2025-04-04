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
        Your task is to summarize an abstract into 5 sentences at most. 
        Avoid technical jargon and explain it in the simplest of words.
        summarize those reviews into 5 lines while  trying to maintain a proper balance between the pros and cons of the product.If either pros or cons dont exist,move on with summarizing it.
        you will be given a list of reviews and when possible a ai summary review. analyze both of these and generate a honest non-biased review while maintaining factual accuracy.
        Your Response will only contain words about the review and nothing else.
        If no postive or negative reviews or there is nothing of factual knowledge or useful response to return, return "".
        Ai Review:{product.ai_review}
        list of reviews:{all_descriptions}
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
