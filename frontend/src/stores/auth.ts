import { defineStore } from "pinia";
import { api } from "../services/api";

export type User = {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
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
      state.user ? `${state.user.first_name || ""} ${state.user.last_name || ""}`.trim() : "",
  },

  actions: {
    // ✅ restauration de session au refresh
    async initFromStorage() {
      const access = localStorage.getItem(ACCESS_KEY);
      const refresh = localStorage.getItem(REFRESH_KEY);

      // si pas de tokens => pas connecté
      if (!access && !refresh) {
        this.user = null;
        return;
      }

      // on tente /me (si access expiré, api.ts va refresh automatiquement)
      try {
        await this.fetchMe();
      } catch (e) {
        // si même après refresh ça échoue => tokens invalides
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

    async login(username: string, password: string) {
      this.loading = true;
      this.lastError = "";

      try {
        const res = await api.post<LoginResponse>("auth/login/", { username, password });

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

    async register(payload: any) {
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
  },
});
