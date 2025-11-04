from rest_framework.routers import DefaultRouter
from .views import PetImageViewSet

router = DefaultRouter()
router.register(r'gallery', PetImageViewSet, basename='gallery')

urlpatterns = router.urls
