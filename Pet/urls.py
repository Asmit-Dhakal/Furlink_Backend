from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PetViewSet, AdoptionViewSet, CategoryViewSet, AdoptionPriceViewSet

router = DefaultRouter()
router.register(r'', PetViewSet, basename='pet')
router.register(r'adoptions', AdoptionViewSet, basename='adoption')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'adoption-prices', AdoptionPriceViewSet, basename='adoptionprice')

urlpatterns = [
    path('', include(router.urls)),
]

