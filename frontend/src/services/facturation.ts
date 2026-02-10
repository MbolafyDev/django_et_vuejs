// src/services/facturation.ts
import { api } from "./api";

/**
 * Ligne de la page Facturation (basée sur Commande)
 */
export type CommandeFacturationRow = {
  id: number;

  // Facture liée à la commande
  facture_id: number | null;
  type_facture: "PROFORMA" | "FACTURE";
  numero_affiche: string;
  is_paid: boolean;

  // Branding
  logo_url: string | null;

  // Paiement
  paiement_statut: "EN_ATTENTE" | "PAYEE" | "ANNULEE";
  paiement_mode: string;
  paiement_reference: string;
  encaisse_le: string | null;

  // Détails commande
  commande_detail: {
    total_commande?: number;
    total_articles?: number;
    client_nom?: string;
    client_contact?: string;
    client_adresse?: string;
    page_detail?: {
      id?: number;
      nom?: string;
    };
    lignes_detail?: any[];
    [key: string]: any;
  };
};

export const FacturationAPI = {
  /**
   * Liste des commandes facturables
   */
  list(params?: Record<string, any>) {
    return api.get("/facturation/commandes/", { params });
  },

  /**
   * Récupérer le PDF inline en BLOB (token inclus via axios)
   */
  pdfInlineBlob(commandeId: number) {
    return api.get(`/facturation/commandes/${commandeId}/pdf/`, {
      responseType: "blob",
    });
  },

  /**
   * Récupérer le PDF en BLOB (download forcé côté backend)
   */
  pdfDownloadBlob(commandeId: number) {
    return api.get(`/facturation/commandes/${commandeId}/pdf/?download=1`, {
      responseType: "blob",
    });
  },

  /**
   * Télécharger un ZIP de factures sélectionnées
   */
  bulkDownload(commandeIds: number[]) {
    return api.post(
      "/facturation/commandes/bulk-download/",
      { commande_ids: commandeIds },
      { responseType: "blob" }
    );
  },

  /**
   * Télécharger un ZIP de TOUTES les factures
   */
  downloadAll(params?: Record<string, any>) {
    return api.get("/facturation/commandes/download-all/", {
      params,
      responseType: "blob",
    });
  },

  /**
   * ✅ NOUVEAU: 1 seul PDF multi-pages pour la sélection
   * - preview => download=false (inline)
   * - download => download=true (?download=1)
   */
  bulkPdfBlob(commandeIds: number[], download = false) {
    const suffix = download ? "?download=1" : "";
    return api.post(
      `/facturation/commandes/bulk-pdf/${suffix}`,
      { commande_ids: commandeIds },
      { responseType: "blob" }
    );
  },
};
