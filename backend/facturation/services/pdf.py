# facturation/services/pdf.py
from __future__ import annotations

from io import BytesIO
from django.utils import timezone

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import utils
from reportlab.pdfgen import canvas

from facturation.models import Facture, FacturationSettings


def _draw_image(c: canvas.Canvas, img_path: str, x: float, y: float, w: float, h: float):
    try:
        img = utils.ImageReader(img_path)
        iw, ih = img.getSize()
        if iw <= 0 or ih <= 0:
            return
        scale = min(w / iw, h / ih)
        nw, nh = iw * scale, ih * scale
        c.drawImage(img, x, y, width=nw, height=nh, mask="auto", preserveAspectRatio=True, anchor="sw")
    except Exception:
        return


def draw_facture_on_canvas(c: canvas.Canvas, facture: Facture):
    """
    Dessine une facture sur le canvas actuel, puis passe à la page suivante.
    IMPORTANT: ne fait PAS c.save()
    """
    commande = facture.commande
    settings_fact = FacturationSettings.get_solo()

    width, height = A4
    margin = 18 * mm
    y = height - margin

    # -------- HEADER: logo + titre --------
    logo_path = None
    if getattr(commande, "page_id", None) and getattr(commande.page, "logo", None):
        try:
            logo_path = commande.page.logo.path
        except Exception:
            logo_path = None

    if logo_path:
        _draw_image(c, logo_path, margin, y - 22 * mm, 40 * mm, 22 * mm)

    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - margin, y - 6 * mm, commande.page.nom if commande.page_id else "FACTURATION")

    c.setFont("Helvetica-Bold", 16)
    c.drawRightString(width - margin, y - 15 * mm, facture.type_facture)

    c.setFont("Helvetica", 10)
    c.drawRightString(width - margin, y - 22 * mm, f"N°: {facture.numero_affiche}")
    c.drawRightString(width - margin, y - 28 * mm, f"Date: {timezone.localtime(facture.date_emission).strftime('%d/%m/%Y %H:%M')}")

    y = y - 38 * mm
    c.line(margin, y, width - margin, y)
    y -= 10 * mm

    # -------- CLIENT / LIVRAISON --------
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Client")
    c.setFont("Helvetica", 10)
    y -= 6 * mm
    c.drawString(margin, y, f"Nom: {commande.client_nom or '-'}")
    y -= 5 * mm
    c.drawString(margin, y, f"Contact: {commande.client_contact or '-'}")
    y -= 5 * mm
    c.drawString(margin, y, f"Adresse: {commande.client_adresse or '-'}")

    y -= 8 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Livraison")
    c.setFont("Helvetica", 10)
    y -= 6 * mm
    lieu = getattr(commande, "lieu_livraison", None)
    c.drawString(margin, y, f"Lieu: {lieu.nom if lieu else '-'}")
    y -= 5 * mm
    c.drawString(margin, y, f"Précision: {commande.precision_lieu or '-'}")
    y -= 5 * mm
    c.drawString(margin, y, f"Date livraison: {commande.date_livraison.strftime('%d/%m/%Y') if commande.date_livraison else '-'}")

    y -= 10 * mm
    c.line(margin, y, width - margin, y)
    y -= 10 * mm

    # -------- TABLE LIGNES --------
    col_ref = margin
    col_prod = margin + 35 * mm
    col_qte = width - margin - 55 * mm
    col_pu = width - margin - 35 * mm
    col_tot = width - margin

    c.setFont("Helvetica-Bold", 10)
    c.drawString(col_ref, y, "Réf")
    c.drawString(col_prod, y, "Produit")
    c.drawRightString(col_qte, y, "Qte")
    c.drawRightString(col_pu, y, "PU")
    c.drawRightString(col_tot, y, "Total")

    y -= 4 * mm
    c.line(margin, y, width - margin, y)
    y -= 8 * mm

    c.setFont("Helvetica", 10)

    total_articles = 0
    for l in commande.lignes.select_related("article").all().order_by("id"):
        ref = getattr(l.article, "reference", "") or "-"
        prod = getattr(l.article, "nom_produit", "") or "-"
        qte = int(l.quantite or 0)
        pu = int(float(l.prix_vente_unitaire or 0))
        st = int(qte * pu)
        total_articles += st

        if y < 55 * mm:
            # nouvelle page MAIS même facture => on continue
            c.showPage()
            y = height - margin
            c.setFont("Helvetica", 10)

        c.drawString(col_ref, y, str(ref)[:18])
        c.drawString(col_prod, y, str(prod)[:45])
        c.drawRightString(col_qte, y, str(qte))
        c.drawRightString(col_pu, y, f"{pu:,}".replace(",", " "))
        c.drawRightString(col_tot, y, f"{st:,}".replace(",", " "))
        y -= 7 * mm

    y -= 3 * mm
    c.line(margin, y, width - margin, y)
    y -= 10 * mm

    frais_final = int(getattr(commande.frais_livraison, "frais_final", 0) or 0)
    total_commande = int(total_articles) + int(frais_final)

    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width - margin, y, f"Sous-total: {total_articles:,}".replace(",", " "))
    y -= 6 * mm
    c.drawRightString(width - margin, y, f"Frais livraison: {frais_final:,}".replace(",", " "))
    y -= 7 * mm
    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(width - margin, y, f"TOTAL: {total_commande:,}".replace(",", " "))

    # -------- FOOTER --------
    footer_y = 22 * mm
    c.setFont("Helvetica", 9)

    if settings_fact.footer_note:
        c.drawString(margin, footer_y + 10 * mm, settings_fact.footer_note)

    sig_x = width - margin - 65 * mm
    sig_y = footer_y + 2 * mm

    c.setFont("Helvetica", 9)
    c.drawString(sig_x, sig_y + 18 * mm, "Signature")

    if settings_fact.signature_image:
        try:
            _draw_image(c, settings_fact.signature_image.path, sig_x, sig_y + 4 * mm, 55 * mm, 14 * mm)
        except Exception:
            pass

    c.setFont("Helvetica-Bold", 9)
    if settings_fact.signature_nom:
        c.drawString(sig_x, sig_y, settings_fact.signature_nom)
    c.setFont("Helvetica", 9)
    if settings_fact.signature_titre:
        c.drawString(sig_x, sig_y - 4 * mm, settings_fact.signature_titre)

    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, 10 * mm, f"Imprimé le {timezone.now().strftime('%d/%m/%Y %H:%M')}")

    # ✅ fin de facture => page suivante (séparation entre factures)
    c.showPage()


def render_facture_pdf_bytes(facture: Facture) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    draw_facture_on_canvas(c, facture)
    c.save()
    pdf = buf.getvalue()
    buf.close()
    return pdf


def render_factures_merged_pdf_bytes(factures: list[Facture]) -> bytes:
    """
    Plusieurs factures -> un seul PDF multi-pages.
    """
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    for f in factures:
        draw_facture_on_canvas(c, f)

    c.save()
    pdf = buf.getvalue()
    buf.close()
    return pdf
