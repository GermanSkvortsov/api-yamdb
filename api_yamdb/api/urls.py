from django.urls import include, path
from rest_framework.routers import DefaultRouter

from titles.views import CategoryViewSet, GenreViewSet, TitleViewSet
from users.views import UserViewSet, signup, token

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', signup, name='signup'),
    path('v1/auth/token/', token, name='token'),
]
