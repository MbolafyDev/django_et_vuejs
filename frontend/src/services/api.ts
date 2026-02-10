import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000/api/";
const ACCESS_KEY = "access_token";
const REFRESH_KEY = "refresh_token";

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 8000,
});

// ✅ Inject access token sur chaque requête
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_KEY);
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
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

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config;

    // ✅ On refresh uniquement sur 401, et une seule fois par requête
    if (err?.response?.status === 401 && original && !original._retry) {
      original._retry = true;

      const refresh = localStorage.getItem(REFRESH_KEY);

      // Pas de refresh token => déconnexion
      if (!refresh) {
        localStorage.removeItem(ACCESS_KEY);
        localStorage.removeItem(REFRESH_KEY);
        return Promise.reject(err);
      }

      // Si un refresh est déjà en cours, on met en attente
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
        // ⚠️ refresh endpoint SimpleJWT
        const r = await axios.post(`${BASE_URL}auth/refresh/`, { refresh });

        const newAccess = r.data.access;
        localStorage.setItem(ACCESS_KEY, newAccess);

        flushQueue(newAccess);

        original.headers = original.headers || {};
        original.headers.Authorization = `Bearer ${newAccess}`;

        return api(original);
      } catch (e) {
        flushQueue(null);
        localStorage.removeItem(ACCESS_KEY);
        localStorage.removeItem(REFRESH_KEY);
        return Promise.reject(e);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(err);
  }
);
