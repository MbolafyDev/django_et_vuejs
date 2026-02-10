// frontend/src/helpers/roles.ts
import type { UserRole } from "@/stores/auth";

export const ROLES = {
  ADMIN: "ADMIN" as UserRole,
  COMMUNITY_MANAGER: "COMMUNITY_MANAGER" as UserRole,
  COMMERCIALE: "COMMERCIALE" as UserRole,
} as const;

export type Permission =
  // Dashboard
  | "dashboard.view"

  // Commandes
  | "commandes.view"
  | "commandes.create"
  | "commandes.update"
  | "commandes.delete"

  // Encaissement
  | "encaissement.view"
  | "encaissement.encaisser"
  | "encaissement.annuler_paiement"

  // Articles
  | "articles.view"
  | "articles.create"
  | "articles.update"
  | "articles.delete"

  // Clients
  | "clients.view"

  // Achats
  | "achats.view"
  | "achats.create"
  | "achats.update"
  | "achats.delete"

  // Livraison / conflivraison
  | "conflivraison.view"
  | "conflivraison.action"

  // Factures
  | "factures.view"

  // Configuration / Pages / Admin
  | "configuration.view"
  | "pages.manage"
  | "users.manage"
  | "roles.manage";

const ROLE_PERMS: Record<UserRole, Permission[]> = {
  ADMIN: [
    "dashboard.view",

    "commandes.view",
    "commandes.create",
    "commandes.update",
    "commandes.delete",

    "encaissement.view",
    "encaissement.encaisser",
    "encaissement.annuler_paiement",

    "articles.view",
    "articles.create",
    "articles.update",
    "articles.delete",

    "clients.view",

    "achats.view",
    "achats.create",
    "achats.update",
    "achats.delete",

    "conflivraison.view",
    "conflivraison.action",

    "factures.view",

    "configuration.view",
    "pages.manage",
    "users.manage",
    "roles.manage",
  ],

  COMMUNITY_MANAGER: [
    "dashboard.view",

    "commandes.view", // si tu veux qu'il voie les commandes
    // (optionnel) s'il doit créer/modifier commandes, décommente :
    // "commandes.create",
    // "commandes.update",

    "encaissement.view", // optionnel
    // "encaissement.encaisser", // optionnel
    // "encaissement.annuler_paiement", // optionnel

    "articles.view",
    "articles.create",
    "articles.update",
    // suppression article => ADMIN only par défaut

    "clients.view",

    "achats.view", // optionnel
    // "achats.create",
    // "achats.update",
    // "achats.delete",

    "conflivraison.view",
    // actions livraison: je laisse CM voir seulement (à toi de décider)
    // "conflivraison.action",

    "factures.view",
  ],

  COMMERCIALE: [
    "commandes.view",
    "commandes.create",
    "commandes.update",
    // pas de delete

    "encaissement.view",
    "encaissement.encaisser",
    // annuler paiement => je mets ADMIN only par défaut, sinon décommente :
    // "encaissement.annuler_paiement",

    "clients.view",
    "factures.view",

    // pas de dashboard, pas d'articles, pas de config
  ],
};

export function getRole(user: any): UserRole | null {
  const r = user?.role as UserRole | undefined;
  return r || null;
}

/** ✅ route level: "allowed roles" (simple) */
export function canAccess(user: any, allowed: UserRole[] | "ANY_AUTH"): boolean {
  if (allowed === "ANY_AUTH") return !!user;
  const r = getRole(user);
  if (!r) return false;
  return allowed.includes(r);
}

/** ✅ permission level: fine-grained actions */
export function can(user: any, perm: Permission): boolean {
  const r = getRole(user);
  if (!r) return false;
  const perms = ROLE_PERMS[r] || [];
  return perms.includes(perm);
}

/** ✅ page de fallback selon rôle (quand accès refusé) */
export function defaultRouteForRole(role: UserRole | null): { name: string } {
  if (role === ROLES.COMMERCIALE) return { name: "commandes" };
  if (role === ROLES.COMMUNITY_MANAGER) return { name: "dashboard-stats" };
  if (role === ROLES.ADMIN) return { name: "dashboard-stats" };
  return { name: "login" };
}
