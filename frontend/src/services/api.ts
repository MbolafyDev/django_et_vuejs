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

// ✅ util: détecter erreur réseau/timeout (ne pas “déconnecter” sur un simple lag)
function isNetworkError(err: any) {
  return (
    !err?.response && // pas de response HTTP
    (err?.code === "ECONNABORTED" || err?.message?.includes("timeout") || err?.message === "Network Error")
  );
}

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original: any = err?.config;

    if (!original) return Promise.reject(err);

    // ✅ On refresh uniquement sur 401, et une seule fois par requête
    if (err?.response?.status === 401 && !original._retry) {
      original._retry = true;

      const refresh = localStorage.getItem(REFRESH_KEY);

      // Pas de refresh token => on nettoie et on remonte l’erreur
      if (!refresh) {
        console.warn("[AUTH] 401 + no refresh token => clear tokens");
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
        console.warn("[AUTH] 401 => trying refresh...");

        // ✅ refresh (raw, sans interceptors)
        const r = await raw.post("auth/refresh/", { refresh });

        // ✅ compat: access OU access_token
        const newAccess = r?.data?.access || r?.data?.access_token || null;

        // ✅ support rotation refresh (si backend renvoie un nouveau refresh)
        const newRefresh = r?.data?.refresh || r?.data?.refresh_token || null;

        console.warn("[AUTH] refresh response:", r?.data);

        if (!newAccess) {
          console.error("[AUTH] refresh OK but no access in response => clear tokens");
          flushQueue(null);
          clearTokens();
          return Promise.reject(err);
        }

        localStorage.setItem(ACCESS_KEY, newAccess);
        if (newRefresh) {
          localStorage.setItem(REFRESH_KEY, newRefresh);
        }

        flushQueue(newAccess);

        // ✅ rejouer la requête originale
        original.headers = original.headers || {};
        original.headers.Authorization = `Bearer ${newAccess}`;

        return api(original);
      } catch (e: any) {
        // ✅ si c'est juste réseau/timeout => on ne supprime pas les tokens (évite déconnexion)
        if (isNetworkError(e)) {
          console.warn("[AUTH] refresh failed due to network/timeout => keep tokens");
          flushQueue(null);
          // on renvoie l'erreur (UI peut afficher "réseau")
          return Promise.reject(e);
        }

        // ✅ refresh token invalide/expiré => là on doit déconnecter
        console.error("[AUTH] refresh failed => clear tokens", e?.response?.status, e?.response?.data);
        flushQueue(null);
        clearTokens();
        return Promise.reject(e);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(err);
  }
);
