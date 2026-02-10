# dashboard/serializers.py
from __future__ import annotations
from rest_framework import serializers


class DashboardOverviewSerializer(serializers.Serializer):
    # compteurs
    nb_commandes = serializers.IntegerField()
    nb_livrees = serializers.IntegerField()
    nb_annulees = serializers.IntegerField()

    # CA (en Ariary, int)
    ca_total_commandes = serializers.IntegerField()
    ca_total_encaisse = serializers.IntegerField()

    panier_moyen = serializers.IntegerField()
    panier_moyen_encaisse = serializers.IntegerField()


class SeriePointSerializer(serializers.Serializer):
    x = serializers.CharField()   # date ISO (YYYY-MM-DD)
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
