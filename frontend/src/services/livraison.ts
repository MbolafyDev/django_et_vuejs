import { api } from "./api";
import type { PaginatedResponse } from "./pagination";

export type LieuCategorie = "VILLE" | "PERIPHERIE" | "PLUS_PERIPHERIE" | "PROVINCE" | "AUTRE";

export type LieuLivraison = {
  id: number;
  nom: string;
  categorie: LieuCategorie;
  actif: boolean;
  default_frais: number;
  created_at?: string;
  updated_at?: string;
};

export type FraisLivraison = {
  id: number;
  lieu: number;
  lieu_detail: LieuLivraison;
  frais_calcule: number; // ✅ sans accent
  frais_override: number | null;
  frais_final: number;
  note: string;
  created_at?: string;
  updated_at?: string;
};

type ListOrPaginated<T> = T[] | PaginatedResponse<T>;

export const LivraisonAPI = {
  // Lieux
  listLieux(params?: any) {
    return api.get<ListOrPaginated<LieuLivraison>>("/livraison/lieux/", { params });
  },
  createLieu(payload: { nom: string; categorie: LieuCategorie; actif?: boolean }) {
    return api.post<LieuLivraison>("/livraison/lieux/", payload);
  },
  updateLieu(id: number, payload: Partial<{ nom: string; categorie: LieuCategorie; actif: boolean }>) {
    return api.patch<LieuLivraison>(`/livraison/lieux/${id}/`, payload);
  },
  removeLieu(id: number) {
    return api.delete(`/livraison/lieux/${id}/`);
  },

  // Frais
  listFrais(params?: any) {
    return api.get<ListOrPaginated<FraisLivraison>>("/livraison/frais/", { params });
  },
  calculer(payload: { lieu: number; frais_override?: number | null }) {
    return api.post("/livraison/frais/calculer/", payload);
  },
  createFrais(payload: { lieu: number; frais_override?: number | null; note?: string }) {
    return api.post<FraisLivraison>("/livraison/frais/", payload);
  },
  updateFrais(id: number, payload: Partial<{ lieu: number; frais_override: number | null; note: string }>) {
    return api.patch<FraisLivraison>(`/livraison/frais/${id}/`, payload);
  },
  removeFrais(id: number) {
    return api.delete(`/livraison/frais/${id}/`);
  },
};
