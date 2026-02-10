// frontend/src/router/guards/roles.ts
import type { NavigationGuardNext, RouteLocationNormalized } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { canAccess, defaultRouteForRole } from "@/helpers/roles";
import type { UserRole } from "@/stores/auth";

export function requireAuth(to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) {
  const auth = useAuthStore();
  if (!auth.isAuthenticated) return next({ name: "login", query: { next: to.fullPath } });
  return next();
}

export function requireRole(allowed: UserRole[] | "ANY_AUTH") {
  return (to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
    const auth = useAuthStore();

    if (!auth.isAuthenticated) return next({ name: "login", query: { next: to.fullPath } });

    if (!canAccess(auth.user, allowed)) {
      const role = auth.user?.role || null;
      return next(defaultRouteForRole(role));
    }

    return next();
  };
}
