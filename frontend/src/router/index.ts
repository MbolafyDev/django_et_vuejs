// frontend/src/router/index.ts
import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

import LoginView from "../views/auth/LoginView.vue";
import RegisterView from "../views/auth/RegisterView.vue";
import ForgotPasswordView from "../views/auth/ForgotPasswordView.vue";
import ResetPasswordView from "../views/auth/ResetPasswordView.vue";

import DashboardView from "../views/DashboardView.vue";
import ClientsView from "../views/clients/ClientsView.vue";
import ArticlesView from "../views/article/ArticlesView.vue";

import LivraisonLieuxView from "@/views/livraison/LivraisonLieuxView.vue";
import LivraisonFraisView from "@/views/livraison/LivraisonFraisView.vue";

import AchatsView from "@/views/achats/AchatsView.vue";
import CommandesView from "@/views/vente/CommandesView.vue";

import EncaissementListView from "@/views/encaissement/EncaissementListView.vue";
import EncaisserCommandeView from "@/views/encaissement/EncaisserCommandeView.vue";

import ConfigurationDashboardView from "@/views/configuration/ConfigurationDashboardView.vue";
import ConfigurationPagesView from "@/views/configuration/ConfigurationPagesView.vue";
import ConfigurationPageFormView from "@/views/configuration/ConfigurationPageFormView.vue";

import FacturesView from "@/views/facturation/FacturesView.vue";

// ✅ NEW: dashboard statistiques (charts)
import DashboardStatsView from "@/views/dashboard/DashboardStatsView.vue";

import ConflivraisonListView from "@/views/conflivraison/ConflivraisonListView.vue";

const routes = [
  { path: "/", redirect: "/dashboard" },

  // Auth
  { path: "/login", name: "login", component: LoginView, meta: { guestOnly: true } },
  { path: "/register", name: "register", component: RegisterView, meta: { guestOnly: true } },
  { path: "/forgot-password", name: "forgot-password", component: ForgotPasswordView, meta: { guestOnly: true } },
  { path: "/reset-password", name: "reset-password", component: ResetPasswordView, meta: { guestOnly: true } },

  // Dashboard & base
  { path: "/dashboard", name: "dashboard", component: DashboardView, meta: { requiresAuth: true } },

  // ✅ NEW: Dashboard Stats (charts)
  { path: "/dashboard-stats", name: "dashboard-stats", component: DashboardStatsView, meta: { requiresAuth: true } },

  { path: "/clients", name: "clients", component: ClientsView, meta: { requiresAuth: true } },
  { path: "/articles", name: "articles", component: ArticlesView, meta: { requiresAuth: true } },

  // ✅ LIVRAISON (paramètres)
  { path: "/parametres/livraison/lieux", name: "livraison_lieux", component: LivraisonLieuxView, meta: { requiresAuth: true } },
  { path: "/parametres/livraison/frais", name: "livraison_frais", component: LivraisonFraisView, meta: { requiresAuth: true } },

  // Achats
  { path: "/achats", name: "achats", component: AchatsView, meta: { requiresAuth: true } },

  // Ventes
  { path: "/commandes", name: "commandes", component: CommandesView, meta: { requiresAuth: true } },

  // Encaissement
  { path: "/encaissement", name: "encaissement_list", component: EncaissementListView, meta: { requiresAuth: true } },
  { path: "/encaissement/encaisser/:id", name: "encaissement_encaisser", component: EncaisserCommandeView, props: true, meta: { requiresAuth: true } },

  // Configuration
  { path: "/configuration", name: "configuration_dashboard", component: ConfigurationDashboardView, meta: { requiresAuth: true } },
  { path: "/configuration/pages", name: "configuration_pages", component: ConfigurationPagesView, meta: { requiresAuth: true } },
  { path: "/configuration/pages/new", name: "configuration_pages_new", component: ConfigurationPageFormView, props: { mode: "create" }, meta: { requiresAuth: true } },
  {
    path: "/configuration/pages/:id/edit",
    name: "configuration_pages_edit",
    component: ConfigurationPageFormView,
    props: (route: any) => ({ mode: "edit", id: Number(route.params.id) }),
    meta: { requiresAuth: true },
  },

  // Facturation
  { path: "/factures", name: "factures", component: FacturesView, meta: { requiresAuth: true } },

  { path: "/conflivraison", name: "conflivraison", component: ConflivraisonListView,  meta: { requiresAuth: true }, },

  // ✅ catch-all TOUJOURS À LA FIN
  { path: "/:pathMatch(.*)*", redirect: "/dashboard" },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();

  // ✅ si token présent, on recharge l’utilisateur
  if (!auth.user && localStorage.getItem("access_token")) {
    try {
      await auth.fetchMe();
    } catch (e) {
      console.warn("fetchMe failed => redirect login", e);
      await auth.logout();
      return { name: "login", query: { next: to.fullPath } };
    }
  }

  // ✅ pages protégées
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: "login", query: { next: to.fullPath } };
  }

  // ✅ pages guest-only
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { name: "dashboard" };
  }

  return true;
});

export default router;
