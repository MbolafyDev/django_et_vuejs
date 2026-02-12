import { computed, onMounted, ref } from "vue";
import { ClientsAPI } from "@/services/clients";

export type Client = {
  id: number;
  nom: string;
  adresse: string;
  contact: string;
};

export function useClientsView() {
  const loading = ref(false);
  const error = ref("");

  const clients = ref<Client[]>([]);
  const search = ref("");

  const filteredClients = computed(() => {
    const q = search.value.trim().toLowerCase();
    if (!q) return clients.value;
    return clients.value.filter((c) => {
      return (
        (c.nom || "").toLowerCase().includes(q) ||
        (c.adresse || "").toLowerCase().includes(q) ||
        (c.contact || "").toLowerCase().includes(q)
      );
    });
  });

  const form = ref<{ id?: number; nom: string; adresse: string; contact: string }>({
    nom: "",
    adresse: "",
    contact: "",
  });

  const isEditing = computed(() => !!form.value.id);

  function resetForm() {
    form.value = { nom: "", adresse: "", contact: "" };
    error.value = "";
  }

  async function loadClients() {
    loading.value = true;
    error.value = "";
    try {
      const res = await ClientsAPI.list();
      // ⚠️ si ton API renvoie {results:[]}, remplace par res.data.results
      clients.value = res.data;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || "Impossible de charger les clients.";
    } finally {
      loading.value = false;
    }
  }

  function startCreate() {
    resetForm();
  }

  function startEdit(c: Client) {
    error.value = "";
    form.value = {
      id: c.id,
      nom: c.nom || "",
      adresse: c.adresse || "",
      contact: c.contact || "",
    };
  }

  async function submit() {
    error.value = "";

    if (!form.value.nom.trim()) {
      error.value = "Le champ 'nom' est obligatoire.";
      return;
    }

    loading.value = true;
    try {
      if (!form.value.id) {
        const res = await ClientsAPI.create({
          nom: form.value.nom.trim(),
          adresse: form.value.adresse.trim(),
          contact: form.value.contact.trim(),
        });
        clients.value = [res.data, ...clients.value];
        resetForm();
      } else {
        const id = form.value.id;
        const res = await ClientsAPI.update(id, {
          nom: form.value.nom.trim(),
          adresse: form.value.adresse.trim(),
          contact: form.value.contact.trim(),
        });
        clients.value = clients.value.map((c) => (c.id === id ? res.data : c));
        resetForm();
      }
    } catch (e: any) {
      const data = e?.response?.data;
      if (data && typeof data === "object") {
        const firstKey = Object.keys(data)[0];
        error.value = firstKey ? `${firstKey}: ${data[firstKey]?.[0] ?? ""}` : "Erreur validation.";
      } else {
        error.value = e?.message || "Erreur lors de l'enregistrement.";
      }
    } finally {
      loading.value = false;
    }
  }

  async function removeClient(c: Client) {
    const ok = confirm(`Supprimer le client "${c.nom}" ?`);
    if (!ok) return;

    loading.value = true;
    error.value = "";
    try {
      await ClientsAPI.remove(c.id);
      clients.value = clients.value.filter((x) => x.id !== c.id);
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || "Impossible de supprimer le client.";
    } finally {
      loading.value = false;
    }
  }

  onMounted(loadClients);

  return {
    loading,
    error,
    clients,
    search,
    filteredClients,

    form,
    isEditing,

    resetForm,
    loadClients,
    startCreate,
    startEdit,
    submit,
    removeClient,
  };
}
