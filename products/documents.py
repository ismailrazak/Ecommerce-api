from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry

from .models import Product


@registry.register_document
class ProductDocument(Document):
    category = fields.TextField(
        attr="get_category_display", fields={"suggest": fields.Completion()}
    )
    name = fields.TextField(attr="name", fields={"suggest": fields.Completion()})

    class Index:
        name = "products"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Product

        fields = ["id", "description", "price"]
