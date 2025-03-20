from elasticsearch_dsl import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from products.documents import ProductDocument
from products.serializers import CustomerProductSerializer


class SearchProductsView(APIView):

    def get(self,request,query,pk=None):
        q = Q("multi_match",query=query,fields=['name','description','category'],fuzziness="auto",)
        search=ProductDocument.search().query(q)
        serializer = CustomerProductSerializer(search.to_queryset(),many=True,context={'request': request})
        return Response(serializer.data,status=status.HTTP_200_OK)
