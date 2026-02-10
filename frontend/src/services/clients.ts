// frontend/src/services/clients.ts
import { api } from "./api";

export const ClientsAPI = {
  list() {
    return api.get("clients/");
  },
  create(payload: { nom: string; adresse?: string; contact?: string }) {
    return api.post("clients/", payload);
  },
  retrieve(id: number) {
    return api.get(`clients/${id}/`);
  },
  update(id: number, payload: { nom: string; adresse?: string; contact?: string }) {
    return api.put(`clients/${id}/`, payload);
  },
  patch(id: number, payload: Partial<{ nom: string; adresse: string; contact: string }>) {
    return api.patch(`clients/${id}/`, payload);
  },
  remove(id: number) {
    return api.delete(`clients/${id}/`);
  },
};
