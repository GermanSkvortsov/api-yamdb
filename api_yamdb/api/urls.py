"""Главный API роутер."""

from django.urls import include, path

urlpatterns = [
    path('', include('users.urls')),

    # TODO: позже добавим titles, reviews и т.д.
    # path('', include('titles.urls')),
    # path('', include('reviews.urls')),
]
