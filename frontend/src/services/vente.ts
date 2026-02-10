// frontend/src/services/vente.ts
import { api } from "./api";

/** ✅ Statuts commande (alignés backend) */
export type CommandeStatut =
  | "EN_ATTENTE"
  | "EN_LIVRAISON"
  | "LIVREE"
  | "ANNULEE";

export type ArticleSuggest = {
  id: number;
  nom_produit: string;
  reference: string;
  prix_vente: number | string;
  quantite_stock: number;
  photo_url?: string | null;
};

export type ClientSuggest = {
  id: number;
  nom: string;
  contact?: string | null;
};

export type LieuCategorie =
  | "VILLE"
  | "PERIPHERIE"
  | "PLUS_PERIPHERIE"
  | "PROVINCE"
  | "AUTRE";

export type LieuSuggest = {
  id: number;
  nom: string;
  categorie: LieuCategorie;
  default_frais: number;
  actif?: boolean;
};

export type PageOption = {
  id: number;
  nom: string;
  lien: string;
  logo_url?: string | null;
  actif?: boolean;
};

export type CommandeLignePayload = {
  article: number;
  quantite: number;
};

export type ClientInput = {
  id?: number;
  nom?: string;
  contact?: string | null;
};

export type LieuInput = {
  id?: number;
  nom?: string;
};

export type CommandePayload = {
  page?: number | null;

  // ✅ statut retiré du payload (géré par backend)
  // statut?: CommandeStatut;

  note?: string;
  precision_lieu?: string;

  date_livraison?: string | null;

  client_input: ClientInput;
  lieu_input: LieuInput;
  frais_override?: number | null;

  lignes: CommandeLignePayload[];
};

export type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type ClientLastLieu = {
  lieu_id: number;
  lieu_nom: string;
  frais_auto: number;
  precision_lieu: string;
} | null;

function toInt(v: any): number | null {
  if (v === null || v === undefined || v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

export const VenteAPI = {
  list(params?: any) {
    return api.get<PaginatedResponse<any>>("/vente/commandes/", { params });
  },

  create(payload: CommandePayload) {
    return api.post("/vente/commandes/", payload);
  },
  update(id: number, payload: CommandePayload) {
    return api.put(`/vente/commandes/${id}/`, payload);
  },
  remove(id: number) {
    return api.delete(`/vente/commandes/${id}/`);
  },

  suggestArticles(q: string) {
    return api.get<ArticleSuggest[]>("/vente/commandes/suggest/articles/", { params: { q } });
  },
  suggestClients(q: string) {
    return api.get<ClientSuggest[]>("/vente/commandes/suggest/clients/", { params: { q } });
  },
  suggestLieux(q: string) {
    return api.get<LieuSuggest[]>("/vente/commandes/suggest/lieux/", { params: { q } });
  },

  getClientLastLieu(client_id: number) {
    return api.get<ClientLastLieu>("/vente/commandes/client-last-lieu/", { params: { client_id } });
  },

  async listPagesActives() {
    const res = await api.get<any>("/configuration/pages/", { params: { actif: "true" } });

    if (res?.data && Array.isArray(res.data.results)) {
      res.data = res.data.results;
      return res as { data: PageOption[] };
    }
    if (Array.isArray(res?.data)) return res as { data: PageOption[] };
    return { data: [] as PageOption[] };
  },

  normalizePageId(value: any): number | null {
    return toInt(value);
  },
};
