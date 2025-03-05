from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()
router.register('all_products',views.CustomerProductViewSet)
router.register('seller_products',views.SellerProductViewSet,basename='products')
urlpatterns = router.urls
