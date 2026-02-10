# vente/serializers.py
from __future__ import annotations

from typing import Any
from django.db import transaction
from rest_framework import serializers

from vente.models import Commande, LigneCommande
from client.models import Client
from article.models import Article
from livraison.models import LieuLivraison, FraisLivraison, default_frais_par_categorie
from configuration.models import Page, AppConfiguration


class ArticleLiteSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ["id", "nom_produit", "reference", "prix_vente", "quantite_stock", "photo_url"]

    def get_photo_url(self, obj: Article) -> str | None:
        request = self.context.get("request")
        if not obj.photo:
            return None
        url = obj.photo.url
        return request.build_absolute_uri(url) if request else url


class ClientLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "nom", "contact"]


class LieuLivraisonLiteSerializer(serializers.ModelSerializer):
    default_frais = serializers.SerializerMethodField()

    class Meta:
        model = LieuLivraison
        fields = ["id", "nom", "categorie", "default_frais"]

    def get_default_frais(self, obj: LieuLivraison) -> int:
        return int(default_frais_par_categorie(obj.categorie))


class PageLiteSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ["id", "nom", "lien", "logo_url"]

    def get_logo_url(self, obj: Page):
        if not obj.logo:
            return None
        request = self.context.get("request")
        url = obj.logo.url
        return request.build_absolute_uri(url) if request else url


class LigneCommandeReadSerializer(serializers.ModelSerializer):
    article_detail = serializers.SerializerMethodField()
    sous_total = serializers.IntegerField(read_only=True)

    class Meta:
        model = LigneCommande
        fields = ["id", "article", "article_detail", "quantite", "prix_vente_unitaire", "sous_total"]

    def get_article_detail(self, obj: LigneCommande):
        return ArticleLiteSerializer(obj.article, context=self.context).data


class ClientInputSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    nom = serializers.CharField(required=False, allow_blank=False)
    contact = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        if not attrs.get("id") and not attrs.get("nom"):
            raise serializers.ValidationError("client_input: fournir id ou nom.")
        return attrs


class LieuInputSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    nom = serializers.CharField(required=False, allow_blank=False)

    def validate(self, attrs):
        if not attrs.get("id") and not attrs.get("nom"):
            raise serializers.ValidationError("lieu_input: fournir id ou nom.")
        return attrs


class LigneCommandeWriteSerializer(serializers.Serializer):
    article = serializers.IntegerField()
    quantite = serializers.IntegerField(min_value=1)

    def validate_article(self, value: int) -> int:
        if not Article.objects.filter(id=value).exists():
            raise serializers.ValidationError("Article introuvable.")
        return value


class CommandeSerializer(serializers.ModelSerializer):
    lignes_detail = LigneCommandeReadSerializer(source="lignes", many=True, read_only=True)
    client_detail = ClientLiteSerializer(source="client", read_only=True)
    lieu_detail = LieuLivraisonLiteSerializer(source="lieu_livraison", read_only=True)
    page_detail = PageLiteSerializer(source="page", read_only=True)

    total_articles = serializers.IntegerField(read_only=True)
    total_commande = serializers.IntegerField(read_only=True)
    frais_final = serializers.SerializerMethodField()

    # ✅ date commande (read-only)
    date_commande = serializers.SerializerMethodField()

    # ✅ statut affiché seulement (pas modifiable via API)
    statut = serializers.CharField(read_only=True)

    # write
    page = serializers.PrimaryKeyRelatedField(queryset=Page.objects.all(), required=False, allow_null=True)

    client_input = ClientInputSerializer(write_only=True)
    lieu_input = LieuInputSerializer(write_only=True)
    frais_override = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    lignes = LigneCommandeWriteSerializer(many=True, write_only=True)

    class Meta:
        model = Commande
        fields = [
            "id",
            "page",
            "page_detail",

            # ✅ read-only (toujours EN_ATTENTE à la création)
            "statut",

            # ✅ dates
            "date_commande",
            "date_livraison",

            "note",
            "precision_lieu",

            "client_nom",
            "client_contact",
            "client_adresse",

            "client_detail",
            "lieu_detail",
            "lignes_detail",

            "total_articles",
            "frais_final",
            "total_commande",

            "client_input",
            "lieu_input",
            "frais_override",
            "lignes",

            "created_at",
            "updated_at",
        ]

    def get_date_commande(self, obj: Commande):
        return obj.created_at.date().isoformat() if obj.created_at else None

    def validate_page(self, value: Page | None):
        if value is None:
            return None
        cfg = AppConfiguration.get_solo()
        if value.config_id != cfg.id:
            raise serializers.ValidationError("Page invalide (pas dans la configuration actuelle).")
        if not value.actif:
            raise serializers.ValidationError("Page inactive.")
        return value

    def get_frais_final(self, obj: Commande) -> int:
        return int(getattr(obj.frais_livraison, "frais_final", 0) or 0)

    def _get_or_create_client(self, data: dict) -> Client:
        cid = data.get("id")
        if cid:
            return Client.objects.get(id=cid)

        nom = (data.get("nom") or "").strip()
        contact = (data.get("contact") or "").strip()

        qs = Client.objects.filter(nom__iexact=nom)
        if contact:
            qs = qs.filter(contact__iexact=contact)

        client = qs.first()
        if client:
            if contact and not (client.contact or "").strip():
                client.contact = contact
                client.save(update_fields=["contact", "updated_at"])
            return client

        return Client.objects.create(nom=nom, contact=contact, adresse="")

    def _get_or_create_lieu(self, data: dict) -> LieuLivraison:
        lid = data.get("id")
        if lid:
            return LieuLivraison.objects.get(id=lid)

        nom = (data.get("nom") or "").strip()
        lieu = LieuLivraison.objects.filter(nom__iexact=nom).first()
        if lieu:
            return lieu

        return LieuLivraison.objects.create(
            nom=nom,
            categorie=LieuLivraison.Categorie.AUTRE,
            actif=True,
        )

    def _build_frais(self, lieu: LieuLivraison, override: int | None) -> FraisLivraison:
        fr = FraisLivraison(lieu=lieu)
        fr.frais_override = override
        fr.save()
        return fr

    def _apply_lines_and_stock(self, commande: Commande, lignes_data: list[dict[str, Any]]):
        for ld in lignes_data:
            article = Article.objects.select_for_update().get(id=ld["article"])
            qte = int(ld["quantite"])

            LigneCommande.objects.create(
                commande=commande,
                article=article,
                quantite=qte,
                prix_vente_unitaire=article.prix_vente,
            )

            article.quantite_stock = int(article.quantite_stock) - qte
            article.save(update_fields=["quantite_stock", "updated_at"])

    def _rollback_stock_from_existing_lines(self, commande: Commande):
        old_lines = list(commande.lignes.select_related("article").all())
        for l in old_lines:
            art = l.article
            art.quantite_stock = int(art.quantite_stock) + int(l.quantite)
            art.save(update_fields=["quantite_stock", "updated_at"])
        commande.lignes.all().delete()

    @transaction.atomic
    def create(self, validated_data):
        # ✅ on ignore toute tentative d'envoyer "statut"
        validated_data.pop("statut", None)

        client_data = validated_data.pop("client_input")
        lieu_data = validated_data.pop("lieu_input")
        override = validated_data.pop("frais_override", None)
        lignes_data = validated_data.pop("lignes", [])
        page_obj = validated_data.pop("page", None)

        request = self.context.get("request")
        user = getattr(request, "user", None)

        client = self._get_or_create_client(client_data)
        lieu = self._get_or_create_lieu(lieu_data)
        frais = self._build_frais(lieu, override)

        # ✅ FORCÉ : à la création -> EN_ATTENTE
        commande = Commande.objects.create(
            user=user if user and user.is_authenticated else None,
            page=page_obj,
            client=client,
            lieu_livraison=lieu,
            frais_livraison=frais,
            precision_lieu=validated_data.get("precision_lieu", "") or "",
            date_livraison=validated_data.get("date_livraison"),
            note=validated_data.get("note", "") or "",
            statut=Commande.Statut.EN_ATTENTE,
        )

        self._apply_lines_and_stock(commande, lignes_data)
        commande.refresh_from_db()
        return commande

    @transaction.atomic
    def update(self, instance: Commande, validated_data):
        # ✅ on ignore toute tentative d'envoyer "statut"
        validated_data.pop("statut", None)

        client_data = validated_data.pop("client_input", None)
        lieu_data = validated_data.pop("lieu_input", None)
        override = validated_data.pop("frais_override", None)
        lignes_data = validated_data.pop("lignes", None)

        if "page" in validated_data:
            instance.page = validated_data.get("page")

        if client_data:
            instance.client = self._get_or_create_client(client_data)

        if lieu_data:
            instance.lieu_livraison = self._get_or_create_lieu(lieu_data)

        if lieu_data or ("frais_override" in self.initial_data):
            instance.frais_livraison = self._build_frais(instance.lieu_livraison, override)

        instance.precision_lieu = validated_data.get("precision_lieu", instance.precision_lieu)
        instance.date_livraison = validated_data.get("date_livraison", instance.date_livraison)
        instance.note = validated_data.get("note", instance.note)

        # ✅ si tu veux que même en édition ça reste EN_ATTENTE, on force aussi ici
        instance.statut = Commande.Statut.EN_ATTENTE

        instance.save()

        if lignes_data is not None:
            self._rollback_stock_from_existing_lines(instance)
            self._apply_lines_and_stock(instance, lignes_data)

        instance.refresh_from_db()
        return instance
