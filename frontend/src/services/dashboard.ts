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

  // ✅ nouveaux KPI
  charges_total: number;
  achats_total: number;
  depenses_total: number;
  cogs_estime: number;
  benefice_estime: number;
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

// ✅ NOUVEAU
export type ArticleSortant = {
  article_id: number;
  reference: string;
  nom_produit: string;

  quantite: number;
  prix_moyen_vente: number;
  total_vente: number;

  cout_unit_estime: number;
  cout_total_estime: number;
  marge_estime: number;
};

export type ArticleEntrant = {
  article_id: number;
  reference: string;
  nom_produit: string;

  quantite: number;
  prix_moyen_achat: number;
  prix_moyen_vente: number;
  total_achat: number;
};

export type ArticlesSortantsResponse = { range: DashboardRange; items: ArticleSortant[] };
export type ArticlesEntrantsResponse = { range: DashboardRange; items: ArticleEntrant[] };

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

  // ✅ nouveaux
  articlesSortants(params?: any) {
    return api.get<ArticlesSortantsResponse>("/dashboard/articles-sortants/", { params }).then(r => r.data);
  },
  articlesEntrants(params?: any) {
    return api.get<ArticlesEntrantsResponse>("/dashboard/articles-entrants/", { params }).then(r => r.data);
  },
};
