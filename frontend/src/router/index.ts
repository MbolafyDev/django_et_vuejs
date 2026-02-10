// frontend/src/router/index.ts
import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

import LoginView from "../views/auth/LoginView.vue";
import RegisterView from "../views/auth/RegisterView.vue";
import ForgotPasswordView from "../views/auth/ForgotPasswordView.vue";
import ResetPasswordView from "../views/auth/ResetPasswordView.vue";

import DashboardView from "../views/DashboardView.vue";
import DashboardStatsView from "../views/dashboard/DashboardStatsView.vue";

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
import ConflivraisonListView from "@/views/conflivraison/ConflivraisonListView.vue";
import ProfileView from "@/views/auth/ProfileView.vue";

// ✅ NEW: Charges
import ChargesView from "@/views/charge/ChargesView.vue";

// ✅ guards
import { requireRole } from "@/router/guards/roles";
import { ROLES, defaultRouteForRole } from "@/helpers/roles";

const routes = [
  // ✅ home dynamique (on gère dans beforeEach)
  { path: "/", name: "home", redirect: "/dashboard-stats" },

  // Auth
  { path: "/login", name: "login", component: LoginView, meta: { guestOnly: true } },
  { path: "/register", name: "register", component: RegisterView, meta: { guestOnly: true } },
  { path: "/forgot-password", name: "forgot-password", component: ForgotPasswordView, meta: { guestOnly: true } },
  { path: "/reset-password", name: "reset-password", component: ResetPasswordView, meta: { guestOnly: true } },

  // Dashboard
  {
    path: "/dashboard",
    name: "dashboard",
    component: DashboardView,
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMUNITY_MANAGER]),
  },
  {
    path: "/dashboard-stats",
    name: "dashboard-stats",
    component: DashboardStatsView,
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMUNITY_MANAGER]),
  },

  // Base
  { path: "/profil", name: "profil", component: ProfileView, meta: { requiresAuth: true } },

  // ✅ NEW: Charges (ADMIN + COMMERCIALE + CM si tu veux)
  {
    path: "/charges",
    name: "charges",
    component: ChargesView,
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMERCIALE, ROLES.COMMUNITY_MANAGER]),
  },

  // Clients (auth + roles)
  {
    path: "/clients",
    name: "clients",
    component: ClientsView,
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMUNITY_MANAGER, ROLES.COMMERCIALE]),
  },

  // Articles (CM + ADMIN)
  {
    path: "/articles",
    name: "articles",
    component: ArticlesView,
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMUNITY_MANAGER]),
  },

  // Achats (ADMIN seulement par défaut)
  {
    path: "/achats",
    name: "achats",
    component: AchatsView,
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN]),
  },

  // Ventes
  {
    path: "/commandes",
    name: "commandes",
    component: CommandesView,
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMERCIALE, ROLES.COMMUNITY_MANAGER]),
  },

  // Encaissement
  {
    path: "/encaissement",
    name: "encaissement_list",
    component: EncaissementListView,
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMERCIALE, ROLES.COMMUNITY_MANAGER]),
  },
  {
    path: "/encaissement/encaisser/:id",
    name: "encaissement_encaisser",
    component: EncaisserCommandeView,
    props: true,
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMERCIALE, ROLES.COMMUNITY_MANAGER]),
  },

  // Livraison (paramètres) — ADMIN
  {
    path: "/parametres/livraison/lieux",
    name: "livraison_lieux",
    component: LivraisonLieuxView,
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN]),
  },
  {
    path: "/parametres/livraison/frais",
    name: "livraison_frais",
    component: LivraisonFraisView,
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN]),
  },

  // Conflivraison
  {
    path: "/conflivraison",
    name: "conflivraison",
    component: ConflivraisonListView,
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMUNITY_MANAGER]),
  },

  // Factures
  {
    path: "/factures",
    name: "factures",
    component: FacturesView,
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMUNITY_MANAGER, ROLES.COMMERCIALE]),
  },

  // Configuration (ADMIN)
  {
    path: "/configuration",
    name: "configuration_dashboard",
    component: ConfigurationDashboardView,
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN]),
  },
  {
    path: "/configuration/pages",
    name: "configuration_pages",
    component: ConfigurationPagesView,
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN]),
  },
  {
    path: "/configuration/pages/new",
    name: "configuration_pages_new",
    component: ConfigurationPageFormView,
    props: { mode: "create" },
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN]),
  },
  {
    path: "/configuration/pages/:id/edit",
    name: "configuration_pages_edit",
    component: ConfigurationPageFormView,
    props: (route: any) => ({ mode: "edit", id: Number(route.params.id) }),
    meta: { requiresAuth: true },
    beforeEnter: requireRole([ROLES.ADMIN]),
  },

  // ✅ catch-all
  { path: "/:pathMatch(.*)*", redirect: "/dashboard-stats" },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();

  // ✅ si token présent, on recharge l’utilisateur
  // IMPORTANT: si ton store utilise "access_token" en clé, garde ça.
  const hasAccess = !!localStorage.getItem("access_token");

  if (!auth.user && hasAccess) {
    try {
      // fetchMe doit gérer le refresh si access expiré (sinon tu seras renvoyé login)
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

  // ✅ guest-only
  if (to.meta.guestOnly && auth.isAuthenticated) {
    const role = auth.user?.role || null;
    return defaultRouteForRole(role);
  }

  // ✅ HOME: si "/" on redirige selon rôle
  if (to.name === "home") {
    const role = auth.user?.role || null;
    return defaultRouteForRole(role);
  }

  return true;
});

export default router;
