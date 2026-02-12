import { onMounted, ref, computed } from "vue";
import { AchatsAPI } from "@/services/achats";
import { ArticlesAPI } from "@/services/articles";
import { unwrapList } from "@/services/pagination";

type Article = {
  id: number;
  nom_produit: string;
  reference: string;
  prix_achat: string;
  prix_vente: string;
  quantite_stock: number;
};

type Achat = any;

export function useAchatsView() {
  const loading = ref(false);
  const error = ref("");

  const achats = ref<Achat[]>([]);
  const articles = ref<Article[]>([]);
  const search = ref("");

  const form = ref<any>({
    id: null as number | null,
    fournisseur: "",
    date_achat: null as string | null,
    note: "",
    lignes: [] as any[],
  });

  const isEditing = computed(() => !!form.value.id);

  const filtered = computed(() => {
    const q = search.value.trim().toLowerCase();
    if (!q) return achats.value;
    return achats.value.filter((x: any) => (x.fournisseur || "").toLowerCase().includes(q));
  });

  function formatAr(value: number | string) {
    const n = typeof value === "string" ? Number(value) : value;
    if (Number.isNaN(n)) return "0 Ar";
    return `${Math.round(n).toLocaleString("fr-FR")} Ar`;
  }

  function resetForm() {
    form.value = { id: null, fournisseur: "", date_achat: null, note: "", lignes: [] };
    error.value = "";
  }

  function addLine() {
    form.value.lignes.push({
      article: null,
      quantite: 1,
      prix_achat_unitaire: 0,
      prix_vente_unitaire: 0,
      maj_prix_article: true,
    });
  }

  function removeLine(idx: number) {
    form.value.lignes.splice(idx, 1);
  }

  function startCreate() {
    resetForm();
    addLine();
  }

  function startEdit(a: any) {
    error.value = "";
    form.value = {
      id: a.id,
      fournisseur: a.fournisseur || "",
      date_achat: a.date_achat || null,
      note: a.note || "",
      lignes: (a.lignes || []).map((l: any) => ({
        article: l.article,
        quantite: l.quantite,
        prix_achat_unitaire: l.prix_achat_unitaire,
        prix_vente_unitaire: l.prix_vente_unitaire,
        maj_prix_article: l.maj_prix_article ?? true,
      })),
    };
    if (form.value.lignes.length === 0) addLine();
  }

  async function loadAll() {
    loading.value = true;
    error.value = "";
    try {
      const [r1, r2] = await Promise.all([AchatsAPI.list(), ArticlesAPI.list()]);
      achats.value = unwrapList<any>(r1.data);
      articles.value = unwrapList<any>(r2.data);
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || "Impossible de charger les données.";
    } finally {
      loading.value = false;
    }
  }

  async function submit() {
    error.value = "";

    if (!form.value.lignes.length) {
      error.value = "Ajoute au moins une ligne.";
      return;
    }
    for (const l of form.value.lignes) {
      if (!l.article) {
        error.value = "Chaque ligne doit avoir un article.";
        return;
      }
      if (!l.quantite || l.quantite < 1) {
        error.value = "Quantité invalide.";
        return;
      }
    }

    loading.value = true;
    try {
      const payload = {
        fournisseur: form.value.fournisseur,
        date_achat: form.value.date_achat,
        note: form.value.note,
        lignes: form.value.lignes,
      };

      if (!form.value.id) await AchatsAPI.create(payload);
      else await AchatsAPI.update(form.value.id, payload);

      resetForm();
      await loadAll();
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

  async function removeAchat(a: any) {
    const ok = confirm(`Supprimer l'achat #${a.id} ? (Cela va enlever le stock ajouté)`);
    if (!ok) return;

    loading.value = true;
    error.value = "";
    try {
      await AchatsAPI.remove(a.id);
      await loadAll();
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || "Impossible de supprimer.";
    } finally {
      loading.value = false;
    }
  }

  onMounted(loadAll);

  return {
    loading,
    error,
    achats,
    articles,
    search,
    filtered,
    form,
    isEditing,
    formatAr,
    resetForm,
    addLine,
    removeLine,
    startCreate,
    startEdit,
    loadAll,
    submit,
    removeAchat,
  };
}
