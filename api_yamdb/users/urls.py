# """URL-маршруты для приложения users."""
#
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
#
# from . import views
#
# router = DefaultRouter()
# router.register(r'users', views.UserViewSet)
#
# urlpatterns = [
#     path('auth/signup/', views.signup, name='signup'),
#     path('auth/token/', views.token, name='token'),
#     path('', include(router.urls)),
# ]
