# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("overview/", views.dashboard_overview, name="dashboard-overview"),
    path("ca-by-day/", views.dashboard_ca_by_day, name="dashboard-ca-by-day"),
    path("commandes-by-statut/", views.dashboard_commandes_by_statut, name="dashboard-commandes-by-statut"),
    path("top-articles/", views.dashboard_top_articles, name="dashboard-top-articles"),
    path("payment-mix/", views.dashboard_payment_mix, name="dashboard-payment-mix"),
    path("sales-by-page/", views.dashboard_sales_by_page, name="dashboard-sales-by-page"),
]
