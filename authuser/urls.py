from django.urls import path
from authuser.views import RegisterViewSet, LoginViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('register', RegisterViewSet, basename='register')
router.register('login', LoginViewSet, basename='login')

urlpatterns = router.urls
