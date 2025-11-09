from authuser.views import RegisterViewSet, LoginViewSet, AccountViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('register', RegisterViewSet, basename='register')
router.register('login', LoginViewSet, basename='login')
router.register('account', AccountViewSet, basename='account')

urlpatterns = router.urls
