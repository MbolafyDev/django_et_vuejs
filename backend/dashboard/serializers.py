# dashboard/serializers.py
from __future__ import annotations
from rest_framework import serializers


class DashboardOverviewSerializer(serializers.Serializer):
    range = serializers.DictField()

    nb_commandes = serializers.IntegerField()
    nb_livrees = serializers.IntegerField()
    nb_annulees = serializers.IntegerField()

    ca_total_commandes = serializers.IntegerField()
    ca_total_encaisse = serializers.IntegerField()

    panier_moyen = serializers.IntegerField()
    panier_moyen_encaisse = serializers.IntegerField()

    # ✅ nouveaux KPI
    charges_total = serializers.IntegerField()
    achats_total = serializers.IntegerField()
    depenses_total = serializers.IntegerField()
    cogs_estime = serializers.IntegerField()
    benefice_estime = serializers.IntegerField()


class SeriePointSerializer(serializers.Serializer):
    x = serializers.CharField()
    y = serializers.IntegerField()


class DashboardSeriesSerializer(serializers.Serializer):
    label = serializers.CharField()
    points = SeriePointSerializer(many=True)


class TopArticleSerializer(serializers.Serializer):
    article_id = serializers.IntegerField()
    reference = serializers.CharField(allow_blank=True)
    nom_produit = serializers.CharField(allow_blank=True)
    quantite = serializers.IntegerField()
    ca = serializers.IntegerField()


class PaymentMixSerializer(serializers.Serializer):
    mode = serializers.CharField()
    nb = serializers.IntegerField()
    ca = serializers.IntegerField()


class StatutCountSerializer(serializers.Serializer):
    statut = serializers.CharField()
    nb = serializers.IntegerField()


class PageSalesSerializer(serializers.Serializer):
    page_id = serializers.IntegerField(allow_null=True)
    page_nom = serializers.CharField(allow_blank=True, allow_null=True)
    nb = serializers.IntegerField()
    ca = serializers.IntegerField()


# ✅ NOUVEAU
class ArticleSortantSerializer(serializers.Serializer):
    article_id = serializers.IntegerField()
    reference = serializers.CharField(allow_blank=True)
    nom_produit = serializers.CharField(allow_blank=True)

    quantite = serializers.IntegerField()
    prix_moyen_vente = serializers.IntegerField()
    total_vente = serializers.IntegerField()

    cout_unit_estime = serializers.IntegerField()
    cout_total_estime = serializers.IntegerField()
    marge_estime = serializers.IntegerField()


class ArticleEntrantSerializer(serializers.Serializer):
    article_id = serializers.IntegerField()
    reference = serializers.CharField(allow_blank=True)
    nom_produit = serializers.CharField(allow_blank=True)

    quantite = serializers.IntegerField()
    prix_moyen_achat = serializers.IntegerField()
    prix_moyen_vente = serializers.IntegerField()
    total_achat = serializers.IntegerField()
