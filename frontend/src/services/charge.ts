import { api } from "./api";

export type ChargeCategorie = {
  id: number;
  nom: string;
  actif: boolean;
  ordre: number;
};

export type Charge = {
  id: number;
  created_at: string;
  updated_at: string;
  date_charge: string;
  categorie: number;
  categorie_nom?: string;
  libelle: string;
  description?: string;
  montant: number | string;
  statut: "BROUILLON" | "PAYEE" | "ANNULEE";
  mode_paiement: "CASH" | "MVOLA" | "ORANGE_MONEY" | "VISA" | "AUTRE";
  commande?: number | null;
  piece_url?: string | null;
  created_by_label?: string | null;
};

export type ChargeCreatePayload = {
  date_charge: string;
  categorie: number;
  libelle: string;
  description?: string;
  montant: number | string;
  statut: Charge["statut"];
  mode_paiement: Charge["mode_paiement"];
  commande?: number | null;
  piece?: File | null;
};

export const ChargeAPI = {
  listCategories(params?: any) {
    return api.get("/charge/categories/", { params });
  },
  createCategory(payload: Partial<ChargeCategorie>) {
    return api.post("/charge/categories/", payload);
  },

  listCharges(params?: any) {
    return api.get("/charge/charges/", { params });
  },
  getCharge(id: number) {
    return api.get(`/charge/charges/${id}/`);
  },
  createCharge(payload: ChargeCreatePayload) {
    const fd = new FormData();
    Object.entries(payload).forEach(([k, v]) => {
      if (v === undefined || v === null) return;
      if (k === "piece" && v instanceof File) fd.append("piece", v);
      else fd.append(k, String(v));
    });
    return api.post("/charge/charges/", fd, { headers: { "Content-Type": "multipart/form-data" } });
  },
  updateCharge(id: number, payload: Partial<ChargeCreatePayload>) {
    const fd = new FormData();
    Object.entries(payload).forEach(([k, v]) => {
      if (v === undefined || v === null) return;
      if (k === "piece" && v instanceof File) fd.append("piece", v);
      else fd.append(k, String(v));
    });
    return api.patch(`/charge/charges/${id}/`, fd, { headers: { "Content-Type": "multipart/form-data" } });
  },
  deleteCharge(id: number) {
    return api.delete(`/charge/charges/${id}/`);
  },
  stats(params?: any) {
    return api.get("/charge/charges/stats/", { params });
  },
};
