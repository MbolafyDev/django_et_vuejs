// src/services/encaissement.ts
import { api } from "./api";

export type PaiementStatut = "EN_ATTENTE" | "PAYEE" | "ANNULEE";
export type ModePaiement = "ESPECE" | "MVOLA" | "ORANGE_MONEY";

export type EncaissementCommande = {
  id: number;
  statut: string;
  date_livraison: string | null;
  client_nom: string;
  client_contact: string;
  total_commande: number;

  paiement_statut: PaiementStatut;
  paiement_mode: string;
  paiement_reference: string;
  encaisse_le: string | null;

  created_at: string;
};

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export const EncaissementAPI = {
  listCommandes(params?: any) {
    return api.get<Paginated<EncaissementCommande>>("/encaissement/commandes/", { params });
  },

  getCommande(id: number) {
    return api.get<EncaissementCommande>(`/encaissement/commandes/${id}/`);
  },

  encaisserCommande(id: number, payload: { mode: ModePaiement; reference?: string; note?: string }) {
    return api.post(`/encaissement/commandes/${id}/encaisser/`, payload);
  },

  annulerPaiement(id: number, payload?: { note?: string }) {
    return api.post(`/encaissement/commandes/${id}/annuler-paiement/`, payload || {});
  },
};
