"""URL-маршруты для приложения users."""

from django.urls import path
from . import views

urlpatterns = [
    path('auth/signup/', views.signup, name='signup'),
]
