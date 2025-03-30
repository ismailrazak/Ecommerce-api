from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from products.documents import ProductDocument


class ProductDocumentSerializer(DocumentSerializer):

    class Meta:
        document = ProductDocument
        fields = ["name", "description", "category", "price"]
