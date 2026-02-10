// src/services/dashboard.ts
import { api } from "./api";

export type DashboardRange = { date_from: string; date_to: string };

export type DashboardOverview = {
  range: DashboardRange;
  nb_commandes: number;
  nb_livrees: number;
  nb_annulees: number;
  ca_total_commandes: number;
  ca_total_encaisse: number;
  panier_moyen: number;
  panier_moyen_encaisse: number;
};

export type SeriePoint = { x: string; y: number };
export type SerieResponse = { range: DashboardRange; label: string; points: SeriePoint[] };

export type StatutCount = { statut: string; nb: number };
export type StatutResponse = { range: DashboardRange; items: StatutCount[] };

export type TopArticle = { article_id: number; reference: string; nom_produit: string; quantite: number; ca: number };
export type TopArticlesResponse = { range: DashboardRange; items: TopArticle[] };

export type PaymentMixItem = { mode: string; nb: number; ca: number };
export type PaymentMixResponse = { range: DashboardRange; items: PaymentMixItem[] };

export type PageSalesItem = { page_id: number | null; page_nom: string | null; nb: number; ca: number };
export type PageSalesResponse = { range: DashboardRange; items: PageSalesItem[] };

export const DashboardAPI = {
  overview(params?: any) {
    return api.get<DashboardOverview>("/dashboard/overview/", { params }).then(r => r.data);
  },
  caByDay(params?: any) {
    return api.get<SerieResponse>("/dashboard/ca-by-day/", { params }).then(r => r.data);
  },
  commandesByStatut(params?: any) {
    return api.get<StatutResponse>("/dashboard/commandes-by-statut/", { params }).then(r => r.data);
  },
  topArticles(params?: any) {
    return api.get<TopArticlesResponse>("/dashboard/top-articles/", { params }).then(r => r.data);
  },
  paymentMix(params?: any) {
    return api.get<PaymentMixResponse>("/dashboard/payment-mix/", { params }).then(r => r.data);
  },
  salesByPage(params?: any) {
    return api.get<PageSalesResponse>("/dashboard/sales-by-page/", { params }).then(r => r.data);
  },
};
