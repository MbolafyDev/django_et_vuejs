# facturation/views.py
from __future__ import annotations

import zipfile
from io import BytesIO

from django.db.models import Prefetch, Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from vente.models import Commande, LigneCommande
from encaissement.models import Encaissement
from facturation.models import Facture
from facturation.serializers import CommandeFacturationSerializer
from facturation.services.pdf import (
    render_facture_pdf_bytes,
    render_factures_merged_pdf_bytes,  # ✅ nouveau (PDF multi-pages)
)


class CommandeFacturationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Facturation = liste des Commandes,
    actions:
    - pdf (1 commande -> 1 PDF)
    - bulk-download (sélection -> ZIP de PDFs)
    - bulk-pdf (sélection -> 1 seul PDF multi-pages)
    - download-all (toutes -> ZIP de PDFs)  ✅ inclus ici pour être complet
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommandeFacturationSerializer

    def get_queryset(self):
        qs = (
            Commande.objects
            .select_related("client", "page", "lieu_livraison", "frais_livraison")
            .select_related("encaissement")
            .select_related("facture")
            .prefetch_related(
                Prefetch("lignes", queryset=LigneCommande.objects.select_related("article")),
            )
            .order_by("-id")
        )

        qp = self.request.query_params
        paiement_statut = (qp.get("paiement_statut") or "").strip()
        vente_statut = (qp.get("statut") or "").strip()
        q = (qp.get("q") or "").strip()

        if vente_statut:
            qs = qs.filter(statut=vente_statut)

        if paiement_statut:
            if paiement_statut == Encaissement.StatutPaiement.EN_ATTENTE:
                qs = qs.filter(
                    Q(encaissement__isnull=True) |
                    Q(encaissement__statut=Encaissement.StatutPaiement.EN_ATTENTE)
                )
            else:
                qs = qs.filter(encaissement__statut=paiement_statut)

        if q:
            qs = qs.filter(
                Q(client_nom__icontains=q) |
                Q(client_contact__icontains=q) |
                Q(id__icontains=q)
            )

        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def _ensure_facture(self, commande: Commande) -> Facture:
        # sécurité: si jamais le signal n'a pas créé
        f, _created = Facture.objects.get_or_create(
            commande=commande,
            defaults={"numero": Facture.build_next_num()},
        )
        return f

    def _validate_ids(self, ids):
        if not isinstance(ids, list) or not ids:
            return None, Response({"detail": "commande_ids requis"}, status=status.HTTP_400_BAD_REQUEST)
        if not all(str(x).isdigit() for x in ids):
            return None, Response({"detail": "commande_ids invalide"}, status=status.HTTP_400_BAD_REQUEST)
        return [int(x) for x in ids], None

    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request, pk=None):
        """
        Voir (inline) ou télécharger (download=1) la facture d'une commande.
        """
        commande = self.get_object()
        facture = self._ensure_facture(commande)

        pdf_bytes = render_facture_pdf_bytes(facture)

        download = (request.query_params.get("download") or "").strip() == "1"
        filename = f"{facture.numero_affiche}.pdf".replace("/", "-")

        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = f'{"attachment" if download else "inline"}; filename="{filename}"'
        return resp

    # ✅ NOUVEAU: 1 seul PDF multi-pages pour la sélection
    @action(detail=False, methods=["post"], url_path="bulk-pdf")
    def bulk_pdf(self, request):
        """
        Génère UN seul PDF multi-pages contenant les factures des commandes sélectionnées.
        body = {"commande_ids":[1,2,3]}
        query ?download=1 pour forcer téléchargement
        """
        ids, err_resp = self._validate_ids(request.data.get("commande_ids", []))
        if err_resp:
            return err_resp

        qs = self.get_queryset().filter(id__in=ids).order_by("id")
        if not qs.exists():
            return Response({"detail": "Aucune commande trouvée"}, status=status.HTTP_404_NOT_FOUND)

        factures: list[Facture] = []
        for cmd in qs:
            factures.append(self._ensure_facture(cmd))

        pdf_bytes = render_factures_merged_pdf_bytes(factures)

        download = (request.query_params.get("download") or "").strip() == "1"
        filename = f"factures_selection_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = f'{"attachment" if download else "inline"}; filename="{filename}"'
        return resp

    @action(detail=False, methods=["post"], url_path="bulk-download")
    def bulk_download(self, request):
        """
        Télécharger ZIP de factures par commandes:
        body = {"commande_ids":[1,2,3]}
        """
        ids, err_resp = self._validate_ids(request.data.get("commande_ids", []))
        if err_resp:
            return err_resp

        qs = self.get_queryset().filter(id__in=ids).order_by("id")
        if not qs.exists():
            return Response({"detail": "Aucune commande trouvée"}, status=status.HTTP_404_NOT_FOUND)

        zbuf = BytesIO()
        with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as z:
            for cmd in qs:
                facture = self._ensure_facture(cmd)
                pdf = render_facture_pdf_bytes(facture)
                name = f"{facture.numero_affiche}.pdf".replace("/", "-")
                z.writestr(name, pdf)

        zbuf.seek(0)
        filename = f"factures_selection_{timezone.now().strftime('%Y%m%d_%H%M%S')}.zip"
        resp = HttpResponse(zbuf.read(), content_type="application/zip")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp

    @action(detail=False, methods=["get"], url_path="download-all")
    def download_all(self, request):
        """
        ZIP de toutes les commandes (factures) selon filtres query params.
        """
        qs = self.get_queryset().order_by("id")
        if not qs.exists():
            return Response({"detail": "Aucune commande"}, status=status.HTTP_404_NOT_FOUND)

        zbuf = BytesIO()
        with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as z:
            for cmd in qs:
                facture = self._ensure_facture(cmd)
                pdf = render_facture_pdf_bytes(facture)
                name = f"{facture.numero_affiche}.pdf".replace("/", "-")
                z.writestr(name, pdf)

        zbuf.seek(0)
        filename = f"factures_toutes_{timezone.now().strftime('%Y%m%d_%H%M%S')}.zip"
        resp = HttpResponse(zbuf.read(), content_type="application/zip")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp
