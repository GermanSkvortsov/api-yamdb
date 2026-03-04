"""Главный API роутер."""

from django.urls import include, path

urlpatterns = [
    path('v1/', include('users.urls')),
    # TODO: позже добавим titles, reviews и т.д.
    # path('v1/', include('titles.urls')),
    # path('v1/', include('reviews.urls')),
]
