from elasticsearch_dsl import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from products.documents import ProductDocument
from products.serializers import CustomerProductSerializer
from django_elasticsearch_dsl_drf.constants import LOOKUP_FILTER_RANGE,LOOKUP_QUERY_GTE,LOOKUP_QUERY_IN,SUGGESTER_COMPLETION
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    SearchFilterBackend,
    SuggesterFilterBackend, CompoundSearchFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet

from search.serializers import ProductDocumentSerializer


# class SearchProductsView(APIView):
#     def get(self,request,query,pk=None):
#         q = Q("multi_match",query=query,fields=['name','description','category'],fuzziness="auto",)
#         search=ProductDocument.search().query(q)
#         serializer = CustomerProductSerializer(search.to_queryset(),many=True,context={'request': request})
#         return Response(serializer.data,status=status.HTTP_200_OK)

class ProductDocumentViewSet(DocumentViewSet):
    document = ProductDocument
    serializer_class = ProductDocumentSerializer
    filter_backends = (
        FilteringFilterBackend,
        CompoundSearchFilterBackend,
        SuggesterFilterBackend,
    )
    filter_fields = {
        'price': {
            'field': 'price',
            'lookups': [
                LOOKUP_FILTER_RANGE,
            ],
        },
    }
    search_fields = {"name":{'fuzziness': 'AUTO'},"description":{'fuzziness': 'AUTO'},"category":{'fuzziness': 'AUTO'}}
    suggester_fields = {
        "name_suggest": {"field": "name.suggest", "suggesters": [SUGGESTER_COMPLETION]}, "category_suggest": {"field": "category.suggest", "suggesters": [SUGGESTER_COMPLETION]}
    }

