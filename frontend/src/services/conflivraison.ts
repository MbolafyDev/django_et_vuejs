// src/services/conflivraison.ts
import { api } from "./api";

export type LivraisonStatut =
  | "A_PREPARER"
  | "EN_LIVRAISON"
  | "LIVREE"
  | "ANNULEE"
  | "REPORTEE";

export type LivraisonEvent = {
  id: number;
  from_statut: string;
  to_statut: string;
  message: string;
  meta: any;
  actor: number | null;
  actor_name: string | null;
  created_at: string;
};

export type CommandeProgrammation = {
  id: number;
  statut: string;
  date_livraison: string | null;
  precision_lieu: string;
  client_nom: string;
  client_contact: string;
  client_adresse: string;
  livraison_id: number | null;
  livraison_statut: LivraisonStatut | null;
  date_prevue: string | null;
  created_at: string;
  updated_at: string;
};

export type Livraison = {
  id: number;
  commande: number;
  commande_detail: any;
  statut: LivraisonStatut;
  date_prevue: string | null;
  date_reelle: string | null;
  raison: string;
  commentaire: string;
  updated_by: number | null;
  events: LivraisonEvent[];
  created_at: string;
  updated_at: string;
};

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type LivraisonActionPayload = {
  raison?: string;
  commentaire?: string;
  date_prevue?: string | null;
};

export const ConflivraisonAPI = {
  list(params?: any) {
    return api.get<Paginated<Livraison>>("/conflivraison/livraisons/", { params });
  },

  // ✅ NEW: history details (pour modal Historique)
  history(id: number) {
    return api.get<Livraison>(`/conflivraison/livraisons/${id}/history/`);
  },

  listCommandes(params?: any) {
    return api.get<Paginated<CommandeProgrammation>>(
      "/conflivraison/livraisons/commandes-a-programmer/",
      { params }
    );
  },

  programmerCommande(commande_id: number, date_livraison: string) {
    return api.post("/conflivraison/livraisons/programmer-commande/", {
      commande_id,
      date_livraison,
    });
  },

  setEnLivraison(id: number, payload?: LivraisonActionPayload) {
    return api.post<Livraison>(`/conflivraison/livraisons/${id}/en-livraison/`, payload || {});
  },
  livrer(id: number, payload?: LivraisonActionPayload) {
    return api.post<Livraison>(`/conflivraison/livraisons/${id}/livrer/`, payload || {});
  },
  annuler(id: number, payload?: LivraisonActionPayload) {
    return api.post<Livraison>(`/conflivraison/livraisons/${id}/annuler/`, payload || {});
  },
  reporter(id: number, payload?: LivraisonActionPayload) {
    return api.post<Livraison>(`/conflivraison/livraisons/${id}/reporter/`, payload || {});
  },

  syncFromCommandes() {
    return api.post<{ created: number }>("/conflivraison/livraisons/sync-from-commandes/");
  },
};
