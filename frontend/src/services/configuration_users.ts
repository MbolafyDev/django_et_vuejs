// frontend/src/services/configuration_users.ts
import { api } from "./api";

export type UserRole = "ADMIN" | "UTILISATEUR" | "COMMERCIALE" | "COMMUNITY_MANAGER";

export type UserItem = {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  date_joined?: string;
  last_login?: string | null;
  photo_profil_url?: string | null;
};

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type ListUsersParams = {
  q?: string;
  role?: UserRole | "";
  actif?: "true" | "false" | ""; // UI
  page?: number;
  page_size?: number;
};

function mapListParams(params?: ListUsersParams) {
  if (!params) return params;

  const p: any = { ...params };

  // ✅ Backend attend is_active (si tu utilises filterset_fields = ["is_active"])
  if (p.actif !== undefined && p.actif !== "") {
    p.is_active = p.actif; // "true"/"false"
  }
  delete p.actif;

  // ✅ SearchFilter : param standard DRF = search
  if (p.q) {
    p.search = p.q;
  }
  delete p.q;

  return p;
}

export const ConfigUsersAPI = {
  list(params?: ListUsersParams) {
    return api.get<Paginated<UserItem>>("configuration/users/", { params: mapListParams(params) });
  },

  get(id: number) {
    return api.get<UserItem>(`configuration/users/${id}/`);
  },

  patch(id: number, payload: Partial<UserItem>) {
    return api.patch<UserItem>(`configuration/users/${id}/`, payload);
  },

  setRole(id: number, role: UserRole) {
    return api.patch<UserItem>(`configuration/users/${id}/set-role/`, { role });
  },

  setStatus(id: number, is_active: boolean) {
    return api.patch<UserItem>(`configuration/users/${id}/set-status/`, { is_active });
  },
};
