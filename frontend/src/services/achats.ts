import { api } from "./api";
import type { PaginatedResponse } from "./pagination";

export type AchatLignePayload = {
  article: number;
  quantite: number;
  prix_achat_unitaire: string | number;
  prix_vente_unitaire: string | number;
  maj_prix_article: boolean;
};

export type AchatPayload = {
  fournisseur?: string;
  date_achat?: string | null;
  note?: string;
  lignes: AchatLignePayload[];
};

export type Achat = {
  id: number;
  fournisseur: string;
  date_achat: string | null;
  note: string;
  total: number;
  lignes: any[];
  created_at: string;
  updated_at: string;
};

type ListOrPaginated<T> = T[] | PaginatedResponse<T>;

export const AchatsAPI = {
  list(params?: any) {
    return api.get<ListOrPaginated<Achat>>("/achats/achats/", { params });
  },
  create(payload: AchatPayload) {
    return api.post<Achat>("/achats/achats/", payload);
  },
  update(id: number, payload: AchatPayload) {
    return api.put<Achat>(`/achats/achats/${id}/`, payload);
  },
  remove(id: number) {
    return api.delete(`/achats/achats/${id}/`);
  },
};
