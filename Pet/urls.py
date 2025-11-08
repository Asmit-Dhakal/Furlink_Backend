
from rest_framework.routers import DefaultRouter
from .views import (
    PetViewSet, CategoryViewSet,
    AdoptionViewSet, AdoptionPriceViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'pets', PetViewSet, basename='pet')
router.register(r'adoptions', AdoptionViewSet, basename='adoption')
router.register(r'prices', AdoptionPriceViewSet, basename='adoptionprice')

urlpatterns = router.urls