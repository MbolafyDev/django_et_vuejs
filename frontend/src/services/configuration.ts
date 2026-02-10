// src/services/configuration.ts
import { api } from "./api";

export type AppConfiguration = {
  id: number;
  app_name: string;
  maintenance_mode: boolean;
  maintenance_message: string;
  created_at: string;
  updated_at: string;
};

export type PageConfig = {
  id: number;
  config: number;
  nom: string;
  lien: string;
  logo: string | null;     // pour upload (FormData)
  logo_url: string | null; // pour affichage
  ordre: number;
  actif: boolean;
  created_at: string;
  updated_at: string;
};

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export const ConfigurationAPI = {
  // config globale
  getSolo() {
    return api.get("/configuration/app/solo/");
  },
  patchSolo(payload: Partial<AppConfiguration>) {
    return api.patch("/configuration/app/solo/", payload);
  },

  // pages
  listPages(params?: any) {
    return api.get<Paginated<PageConfig>>("/configuration/pages/", { params });
  },
  getPage(id: number) {
    return api.get<PageConfig>(`/configuration/pages/${id}/`);
  },
  createPage(formData: FormData) {
    return api.post("/configuration/pages/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  updatePage(id: number, formData: FormData) {
    return api.patch(`/configuration/pages/${id}/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  deletePage(id: number) {
    return api.delete(`/configuration/pages/${id}/`);
  },
};
