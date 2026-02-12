import { computed, onMounted, ref } from "vue";
import { LivraisonAPI, type LieuLivraison, type LieuCategorie } from "@/services/livraison";
import { unwrapList } from "@/services/pagination";

export function useLieuxLivraison() {
  const loading = ref(false);
  const error = ref("");
  const lieux = ref<LieuLivraison[]>([]);
  const search = ref("");

  const filteredLieux = computed(() => {
    const q = search.value.trim().toLowerCase();
    if (!q) return lieux.value;
    return lieux.value.filter((x) => (x.nom || "").toLowerCase().includes(q));
  });

  const actifsCount = computed(() => filteredLieux.value.filter((x) => x.actif).length);
  const inactifsCount = computed(() => filteredLieux.value.filter((x) => !x.actif).length);

  const form = ref<{ id?: number; nom: string; categorie: LieuCategorie; actif: boolean }>({
    nom: "",
    categorie: "VILLE",
    actif: true,
  });

  const isEditing = computed(() => !!form.value.id);

  function labelCat(c: LieuCategorie) {
    const map: Record<LieuCategorie, string> = {
      VILLE: "Ville",
      PERIPHERIE: "Périphérie",
      PLUS_PERIPHERIE: "Plus périphérie",
      PROVINCE: "Province",
      AUTRE: "Autre",
    };
    return map[c] || (c as any);
  }

  function formatAr(value: number) {
    return `${Math.round(value || 0).toLocaleString("fr-FR")} Ar`;
  }

  function resetForm() {
    form.value = { nom: "", categorie: "VILLE", actif: true };
    error.value = "";
  }

  function startCreate() {
    resetForm();
  }

  function startEdit(l: LieuLivraison) {
    error.value = "";
    form.value = { id: l.id, nom: l.nom, categorie: l.categorie, actif: l.actif };
  }

  async function loadLieux() {
    loading.value = true;
    error.value = "";
    try {
      const res = await LivraisonAPI.listLieux();
      lieux.value = unwrapList<LieuLivraison>(res.data);
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || "Impossible de charger les lieux.";
    } finally {
      loading.value = false;
    }
  }

  async function submit() {
    error.value = "";
    if (!form.value.nom.trim()) {
      error.value = "Le champ 'nom' est obligatoire.";
      return;
    }

    loading.value = true;
    try {
      const payload = { nom: form.value.nom.trim(), categorie: form.value.categorie, actif: form.value.actif };

      if (!form.value.id) await LivraisonAPI.createLieu(payload);
      else await LivraisonAPI.updateLieu(form.value.id, payload);

      resetForm();
      await loadLieux();
    } catch (e: any) {
      const data = e?.response?.data;
      if (data && typeof data === "object") {
        const k = Object.keys(data)[0];
        error.value = k ? `${k}: ${data[k]?.[0] ?? ""}` : "Erreur validation.";
      } else {
        error.value = e?.message || "Erreur lors de l'enregistrement.";
      }
    } finally {
      loading.value = false;
    }
  }

  async function removeLieu(l: LieuLivraison) {
    const ok = confirm(`Supprimer le lieu "${l.nom}" ?`);
    if (!ok) return;

    loading.value = true;
    error.value = "";
    try {
      await LivraisonAPI.removeLieu(l.id);
      await loadLieux();
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || "Impossible de supprimer le lieu.";
    } finally {
      loading.value = false;
    }
  }

  onMounted(loadLieux);

  return {
    loading, error,
    lieux, search,

    filteredLieux,
    actifsCount, inactifsCount,

    form, isEditing,

    labelCat, formatAr,

    resetForm, startCreate, startEdit,
    loadLieux, submit, removeLieu,
  };
}
