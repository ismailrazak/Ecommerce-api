from django_elasticsearch_dsl import Index
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl import Document,fields

from .models import Product


@registry.register_document
class ProductDocument(Document):
    category = fields.TextField(attr="get_category_display")

    class Index:
        name='products'
        settings ={"number_of_shards":1,"number_of_replicas":0}

    class Django:
        model=Product

        fields=[
            'id','name','description',
        ]