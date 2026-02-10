# client/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("clients/", views.clients_list_create, name="clients_list_create"),
    path("clients/<int:pk>/", views.client_detail, name="client_detail"),
]

