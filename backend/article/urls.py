# articles/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("articles/", views.articles_list_create, name="articles_list_create"),
    path("articles/<int:pk>/", views.article_detail, name="article_detail"),
]
