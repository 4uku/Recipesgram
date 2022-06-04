from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, delete_token, get_token

router = DefaultRouter()
router.register('', UserViewSet, basename='userviewset')

urlpatterns = [
    path('token/login/', get_token, name='get_token'),
    path('token/logout/', delete_token, name='delete_token'),
    path('', include(router.urls))
]
