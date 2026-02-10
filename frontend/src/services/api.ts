// frontend/src/services/api.ts
import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000/api/";
const ACCESS_KEY = "access_token";
const REFRESH_KEY = "refresh_token";

// ✅ Instance principale (avec interceptors)
export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 8000,
});

// ✅ Instance "raw" (sans interceptors) pour refresh
const raw = axios.create({
  baseURL: BASE_URL,
  timeout: 8000,
});

// ✅ Inject access token sur chaque requête
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_KEY);
  if (token) {
    config.headers = config.headers || {};
    (config.headers as any).Authorization = `Bearer ${token}`;
  }
  return config;
});

// ---- Auto refresh logic ----
let isRefreshing = false;
let queue: Array<(token: string | null) => void> = [];

function flushQueue(token: string | null) {
  queue.forEach((cb) => cb(token));
  queue = [];
}

function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original: any = err?.config;

    // ✅ Si pas de config => erreur normale
    if (!original) return Promise.reject(err);

    // ✅ On refresh uniquement sur 401, et une seule fois par requête
    if (err?.response?.status === 401 && !original._retry) {
      original._retry = true;

      const refresh = localStorage.getItem(REFRESH_KEY);

      // Pas de refresh token => on nettoie et on remonte l’erreur
      if (!refresh) {
        clearTokens();
        return Promise.reject(err);
      }

      // ✅ Si un refresh est déjà en cours, on met en attente
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          queue.push((newToken) => {
            if (!newToken) return reject(err);
            original.headers = original.headers || {};
            original.headers.Authorization = `Bearer ${newToken}`;
            resolve(api(original));
          });
        });
      }

      isRefreshing = true;

      try {
        /**
         * ✅ IMPORTANT : on utilise raw (sans interceptors),
         * sinon si refresh renvoie 401 => boucle infinie possible.
         *
         * Ton endpoint actuel:
         * POST /api/auth/refresh/ { refresh }
         * => { access }
         */
        const r = await raw.post("auth/refresh/", { refresh });

        const newAccess = r?.data?.access;

        if (!newAccess) {
          // refresh répondu mais pas d’access => on force logout
          flushQueue(null);
          clearTokens();
          return Promise.reject(err);
        }

        localStorage.setItem(ACCESS_KEY, newAccess);

        // ✅ on libère toutes les requêtes en attente
        flushQueue(newAccess);

        // ✅ on rejoue la requête originale
        original.headers = original.headers || {};
        original.headers.Authorization = `Bearer ${newAccess}`;

        return api(original);
      } catch (e: any) {
        // ✅ refresh failed (refresh expiré, réseau, timeout...)
        flushQueue(null);
        clearTokens();
        return Promise.reject(e);
      } finally {
        isRefreshing = false;
      }
    }

    // ✅ autre erreur => normal
    return Promise.reject(err);
  }
);
