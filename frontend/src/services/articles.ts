import { api } from "./api";

export type Article = {
  id: number;
  nom_produit: string;
  reference: string;
  prix_achat: string | number;
  prix_vente: string | number;
  description: string;
  photo?: string | null;
  photo_url?: string | null;
  created_at?: string;
  updated_at?: string;
};

export const ArticlesAPI = {
  list() {
    return api.get<Article[]>("articles/");
  },

  // ✅ CREATE multipart/form-data
  create(formData: FormData) {
    return api.post<Article>("articles/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  // ✅ UPDATE multipart/form-data
  update(id: number, formData: FormData) {
    return api.put<Article>(`articles/${id}/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  retrieve(id: number) {
    return api.get<Article>(`articles/${id}/`);
  },

  remove(id: number) {
    return api.delete<{ detail?: string }>(`articles/${id}/`);
  },
};
