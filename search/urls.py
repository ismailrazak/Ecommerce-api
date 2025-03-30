from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(
    "product_search", views.ProductDocumentViewSet, basename="product_search"
)

urlpatterns = router.urls
# urlpatterns = [
#     path("search/<str:query>",views.SearchProductsView.as_view())
# ]
