from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PetViewSet, AdoptionViewSet

router = DefaultRouter()
router.register(r'', PetViewSet, basename='pet')
router.register(r'adoptions', AdoptionViewSet, basename='adoption')

urlpatterns = [
    path('', include(router.urls)),
]

