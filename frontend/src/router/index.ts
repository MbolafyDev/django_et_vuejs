import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

// Layout global (Navbar)
import AppLayoutView from "@/layouts/AppLayoutView.vue";

// Auth
import LoginView from "../views/auth/LoginView.vue";
import RegisterView from "../views/auth/RegisterView.vue";
import ForgotPasswordView from "../views/auth/ForgotPasswordView.vue";
import ResetPasswordView from "../views/auth/ResetPasswordView.vue";

// Views
import DashboardView from "../views/DashboardView.vue";
import DashboardStatsView from "@/views/dashboard/DashboardStatsView.vue";
import ClientsView from "../views/clients/ClientsView.vue";
import ArticlesView from "../views/article/ArticlesView.vue";
import LivraisonLieuxView from "@/views/livraison/LivraisonLieuxView.vue";
import LivraisonFraisView from "@/views/livraison/LivraisonFraisView.vue";
import AchatsView from "@/views/achats/AchatsView.vue";
import CommandesView from "@/views/vente/CommandesView.vue";
import EncaissementListView from "@/views/encaissement/EncaissementListView.vue";
import EncaisserCommandeView from "@/views/encaissement/EncaisserCommandeView.vue";
import FacturesView from "@/views/facturation/FacturesView.vue";
import ConflivraisonListView from "@/views/conflivraison/ConflivraisonListView.vue";
import ProfileView from "@/views/auth/ProfileView.vue";
import ChargesView from "@/views/charge/ChargesView.vue";

// Configuration
import ConfigurationDashboardView from "@/views/configuration/ConfigurationDashboardView.vue";
import ConfigurationPagesView from "@/views/configuration/ConfigurationPagesView.vue";
import ConfigurationPageFormView from "@/views/configuration/ConfigurationPageFormView.vue";
import UsersView from "@/views/configuration/UsersView.vue";

// Guards / roles
import { requireRole } from "@/router/guards/roles";
import { ROLES, defaultRouteForRole } from "@/helpers/roles";

const routes = [
  { path: "/", name: "home", redirect: "/dashboard-stats" },

  // Auth (sans navbar)
  { path: "/login", name: "login", component: LoginView, meta: { guestOnly: true } },
  { path: "/register", name: "register", component: RegisterView, meta: { guestOnly: true } },
  { path: "/forgot-password", name: "forgot-password", component: ForgotPasswordView, meta: { guestOnly: true } },
  { path: "/reset-password", name: "reset-password", component: ResetPasswordView, meta: { guestOnly: true } },

  // ✅ APP (avec navbar partout)
  {
    path: "",
    component: AppLayoutView,
    meta: { requiresAuth: true },
    children: [
      // Dashboard
      {
        path: "/dashboard",
        name: "dashboard",
        component: DashboardView,
        beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMUNITY_MANAGER]),
      },
      {
        path: "/dashboard-stats",
        name: "dashboard-stats",
        component: DashboardStatsView,
        beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMUNITY_MANAGER]),
      },

      // Base
      { path: "/profil", name: "profil", component: ProfileView },

      // Charges
      {
        path: "/charges",
        name: "charges",
        component: ChargesView,
        beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMERCIALE, ROLES.COMMUNITY_MANAGER]),
      },

      // Clients
      {
        path: "/clients",
        name: "clients",
        component: ClientsView,
        beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMUNITY_MANAGER, ROLES.COMMERCIALE]),
      },

      // Articles
      {
        path: "/articles",
        name: "articles",
        component: ArticlesView,
        beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMUNITY_MANAGER]),
      },

      // Achats
      {
        path: "/achats",
        name: "achats",
        component: AchatsView,
        beforeEnter: requireRole([ROLES.ADMIN]),
      },

      // Ventes
      {
        path: "/commandes",
        name: "commandes",
        component: CommandesView,
        beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMERCIALE, ROLES.COMMUNITY_MANAGER]),
      },

      // Encaissement
      {
        path: "/encaissement",
        name: "encaissement_list",
        component: EncaissementListView,
        beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMERCIALE, ROLES.COMMUNITY_MANAGER]),
      },
      {
        path: "/encaissement/encaisser/:id",
        name: "encaissement_encaisser",
        component: EncaisserCommandeView,
        props: true,
        beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMERCIALE, ROLES.COMMUNITY_MANAGER]),
      },

      // Livraison
      {
        path: "/parametres/livraison/lieux",
        name: "livraison_lieux",
        component: LivraisonLieuxView,
        beforeEnter: requireRole([ROLES.ADMIN]),
      },
      {
        path: "/parametres/livraison/frais",
        name: "livraison_frais",
        component: LivraisonFraisView,
        beforeEnter: requireRole([ROLES.ADMIN]),
      },

      // Conflivraison
      {
        path: "/conflivraison",
        name: "conflivraison",
        component: ConflivraisonListView,
        beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMUNITY_MANAGER]),
      },

      // Factures
      {
        path: "/factures",
        name: "factures",
        component: FacturesView,
        beforeEnter: requireRole([ROLES.ADMIN, ROLES.COMMUNITY_MANAGER, ROLES.COMMERCIALE]),
      },

      // Configuration (ADMIN)
      {
        path: "/configuration",
        name: "configuration_dashboard",
        component: ConfigurationDashboardView,
        beforeEnter: requireRole([ROLES.ADMIN]),
      },
      {
        path: "/configuration/pages",
        name: "configuration_pages",
        component: ConfigurationPagesView,
        beforeEnter: requireRole([ROLES.ADMIN]),
      },
      {
        path: "/configuration/pages/new",
        name: "configuration_pages_new",
        component: ConfigurationPageFormView,
        props: { mode: "create" },
        beforeEnter: requireRole([ROLES.ADMIN]),
      },
      {
        path: "/configuration/pages/:id/edit",
        name: "configuration_pages_edit",
        component: ConfigurationPageFormView,
        props: (route: any) => ({ mode: "edit", id: Number(route.params.id) }),
        beforeEnter: requireRole([ROLES.ADMIN]),
      },
      {
        path: "/configuration/users",
        name: "configuration_users",
        component: UsersView,
        beforeEnter: requireRole([ROLES.ADMIN]),
      },
    ],
  },

  { path: "/:pathMatch(.*)*", redirect: "/dashboard-stats" },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  const hasAccess = !!localStorage.getItem("access_token");

  // ✅ IMPORTANT: meta sur routes parents => on utilise matched
  const requiresAuth = to.matched.some((r) => (r.meta as any)?.requiresAuth);
  const guestOnly = to.matched.some((r) => (r.meta as any)?.guestOnly);

  if (!auth.user && hasAccess) {
    try {
      await auth.fetchMe();
    } catch (e) {
      console.warn("fetchMe failed => redirect login", e);
      await auth.logout();
      return { name: "login", query: { next: to.fullPath } };
    }
  }

  if (requiresAuth && !auth.isAuthenticated) {
    return { name: "login", query: { next: to.fullPath } };
  }

  if (guestOnly && auth.isAuthenticated) {
    const role = auth.user?.role || null;
    return defaultRouteForRole(role);
  }

  if (to.name === "home") {
    const role = auth.user?.role || null;
    return defaultRouteForRole(role);
  }

  return true;
});

export default router;
