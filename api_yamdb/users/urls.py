"""URL-маршруты для приложения users."""

from django.urls import path

from . import views

urlpatterns = [
    path('auth/signup/', views.signup, name='signup'),
    path('auth/token/', views.token, name='token'),
]
