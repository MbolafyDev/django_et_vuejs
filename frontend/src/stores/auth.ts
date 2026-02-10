import { defineStore } from "pinia";
import { api } from "../services/api";

export type UserRole = "ADMIN" | "COMMERCIALE" | "COMMUNITY_MANAGER";
export type UserSexe = "M" | "F" | "AUTRE" | "";

export type User = {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;

  // ✅ role
  role?: UserRole;

  // ✅ champs profil
  photo_profil_url?: string | null;
  photo_couverture_url?: string | null;
  adresse?: string;
  numero_telephone?: string;
  sexe?: UserSexe;
};

type LoginResponse = {
  access: string;
  refresh: string;
  user?: User;
};

const ACCESS_KEY = "access_token";
const REFRESH_KEY = "refresh_token";

function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY);
}

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as User | null,
    loading: false,
    lastError: "" as string,
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    fullName: (state) =>
      state.user
        ? `${state.user.first_name || ""} ${state.user.last_name || ""}`.trim()
        : "",

    // ✅ helpers role
    isAdmin: (state) => state.user?.role === "ADMIN",
    isCommerciale: (state) => state.user?.role === "COMMERCIALE",
    isCommunityManager: (state) => state.user?.role === "COMMUNITY_MANAGER",
  },

  actions: {
    // ✅ restauration de session au refresh
    async initFromStorage() {
      const access = localStorage.getItem(ACCESS_KEY);
      const refresh = localStorage.getItem(REFRESH_KEY);

      if (!access && !refresh) {
        this.user = null;
        return;
      }

      try {
        await this.fetchMe();
      } catch (e) {
        this.logoutLocalOnly();
      }
    },

    logoutLocalOnly() {
      localStorage.removeItem(ACCESS_KEY);
      localStorage.removeItem(REFRESH_KEY);
      this.user = null;
      this.loading = false;
      this.lastError = "";
    },

    // ✅ LOGIN PAR EMAIL
    async login(email: string, password: string) {
      this.loading = true;
      this.lastError = "";

      try {
        const res = await api.post<LoginResponse>("auth/login/", {
          email,
          password,
        });

        localStorage.setItem(ACCESS_KEY, res.data.access);
        localStorage.setItem(REFRESH_KEY, res.data.refresh);

        if (res.data.user) {
          this.user = res.data.user;
        } else {
          await this.fetchMe();
        }
      } catch (e: any) {
        const data = e?.response?.data;
        this.lastError =
          data?.detail ||
          data?.message ||
          (typeof data === "string" ? data : "") ||
          "Identifiants invalides ou erreur réseau.";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async fetchMe() {
      const res = await api.get<User>("auth/me/");
      this.user = res.data;
    },

    async logout() {
      this.loading = true;
      this.lastError = "";

      const refresh = getRefreshToken();
      try {
        if (refresh) {
          await api.post("auth/logout/", { refresh });
        }
      } catch (e) {
        console.warn("Logout backend error (ignored):", e);
      } finally {
        this.logoutLocalOnly();
      }
    },

    // ✅ REGISTER: first_name, last_name, username, email, password
    async register(payload: {
      first_name: string;
      last_name: string;
      username: string;
      email: string;
      password: string;
    }) {
      this.lastError = "";
      await api.post("auth/register/", payload);
    },

    async forgotPassword(email: string) {
      this.lastError = "";
      return await api.post("auth/forgot-password/", { email });
    },

    async resetPassword(uid: string, token: string, new_password: string) {
      this.lastError = "";
      await api.post("auth/reset-password/", { uid, token, new_password });
    },

    // ✅ UPDATE PROFILE (multipart) : adresse, téléphone, sexe, photo profil/couverture
    async updateProfile(payload: {
      first_name?: string;
      last_name?: string;
      adresse?: string;
      numero_telephone?: string;
      sexe?: UserSexe;
      photo_profil?: File | null;
      photo_couverture?: File | null;
    }) {
      this.lastError = "";
      this.loading = true;

      try {
        const fd = new FormData();

        if (payload.first_name !== undefined) fd.append("first_name", payload.first_name);
        if (payload.last_name !== undefined) fd.append("last_name", payload.last_name);
        if (payload.adresse !== undefined) fd.append("adresse", payload.adresse);
        if (payload.numero_telephone !== undefined) fd.append("numero_telephone", payload.numero_telephone);
        if (payload.sexe !== undefined) fd.append("sexe", payload.sexe);

        if (payload.photo_profil) fd.append("photo_profil", payload.photo_profil);
        if (payload.photo_couverture) fd.append("photo_couverture", payload.photo_couverture);

        // PATCH /auth/profile/
        const res = await api.patch<{ message: string; user: User }>("auth/profile/", fd, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        this.user = res.data.user;
        return res;
      } catch (e: any) {
        const data = e?.response?.data;
        this.lastError =
          data?.detail ||
          data?.message ||
          (typeof data === "string" ? data : "") ||
          "Erreur lors de la mise à jour du profil.";
        throw e;
      } finally {
        this.loading = false;
      }
    },
  },
});
