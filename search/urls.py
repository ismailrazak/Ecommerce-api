from django.urls import path

from . import views
from rest_framework.routers import SimpleRouter

router =SimpleRouter()
router.register('product_search',views.ProductDocumentViewSet,basename='product_search')

urlpatterns = router.urls
# urlpatterns = [
#     path("search/<str:query>",views.SearchProductsView.as_view())
# ]