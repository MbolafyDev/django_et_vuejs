import { onMounted, ref, computed } from "vue";
import { ArticlesAPI } from "@/services/articles";

export type Article = {
  id: number;
  nom_produit: string;
  reference: string;
  prix_achat: string | number;
  prix_vente: string | number;
  description?: string | null;
  photo_url?: string | null;
};

export function useArticlesView() {
  const loading = ref(false);
  const error = ref("");
  const articles = ref<Article[]>([]);
  const search = ref("");

  const filteredArticles = computed(() => {
    const q = search.value.trim().toLowerCase();
    if (!q) return articles.value;
    return articles.value.filter((a) =>
      (a.nom_produit || "").toLowerCase().includes(q) ||
      (a.reference || "").toLowerCase().includes(q)
    );
  });

  const form = ref<{
    id?: number;
    nom_produit: string;
    reference: string;
    prix_achat: string;
    prix_vente: string;
    description: string;
    photo_url?: string | null;
  }>({
    nom_produit: "",
    reference: "",
    prix_achat: "0",
    prix_vente: "0",
    description: "",
    photo_url: null,
  });

  const photoFile = ref<File | null>(null);
  const photoPreview = ref<string | null>(null);

  const isEditing = computed(() => !!form.value.id);

  function formatAr(value: string | number) {
    const n = typeof value === "string" ? Number(value) : value;
    if (Number.isNaN(n)) return "0 Ar";
    return `${Math.round(n).toLocaleString("fr-FR")} Ar`;
  }

  function onPhotoChange(e: Event) {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0] || null;
    photoFile.value = file;

    if (photoPreview.value) URL.revokeObjectURL(photoPreview.value);
    photoPreview.value = file ? URL.createObjectURL(file) : null;
  }

  function resetForm() {
    form.value = {
      nom_produit: "",
      reference: "",
      prix_achat: "0",
      prix_vente: "0",
      description: "",
      photo_url: null,
    };
    error.value = "";

    photoFile.value = null;
    if (photoPreview.value) URL.revokeObjectURL(photoPreview.value);
    photoPreview.value = null;
  }

  async function loadArticles() {
    loading.value = true;
    error.value = "";
    try {
      const res = await ArticlesAPI.list();
      // ⚠️ si ton API renvoie {results:[]}, remplace par res.data.results
      articles.value = res.data;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || "Impossible de charger les articles.";
    } finally {
      loading.value = false;
    }
  }

  function startCreate() {
    resetForm();
  }

  function startEdit(a: Article) {
    error.value = "";
    form.value = {
      id: a.id,
      nom_produit: a.nom_produit || "",
      reference: a.reference || "",
      prix_achat: String(a.prix_achat ?? "0"),
      prix_vente: String(a.prix_vente ?? "0"),
      description: (a.description as any) || "",
      photo_url: a.photo_url ?? null,
    };

    photoFile.value = null;
    if (photoPreview.value) URL.revokeObjectURL(photoPreview.value);
    photoPreview.value = null;
  }

  async function submit() {
    error.value = "";

    if (!form.value.nom_produit.trim()) {
      error.value = "Le champ 'nom_produit' est obligatoire.";
      return;
    }
    if (!form.value.reference.trim()) {
      error.value = "Le champ 'reference' est obligatoire.";
      return;
    }

    loading.value = true;

    const fd = new FormData();
    fd.append("nom_produit", form.value.nom_produit.trim());
    fd.append("reference", form.value.reference.trim());
    fd.append("prix_achat", String(form.value.prix_achat ?? "0"));
    fd.append("prix_vente", String(form.value.prix_vente ?? "0"));
    fd.append("description", form.value.description.trim());

    if (photoFile.value) fd.append("photo", photoFile.value);

    try {
      if (!form.value.id) {
        const res = await ArticlesAPI.create(fd);
        articles.value = [res.data, ...articles.value];
        resetForm();
      } else {
        const id = form.value.id;
        const res = await ArticlesAPI.update(id, fd);
        articles.value = articles.value.map((x) => (x.id === id ? res.data : x));
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

  async function removeArticle(a: Article) {
    const ok = confirm(`Supprimer l'article "${a.nom_produit}" ?`);
    if (!ok) return;

    loading.value = true;
    error.value = "";
    try {
      await ArticlesAPI.remove(a.id);
      articles.value = articles.value.filter((x) => x.id !== a.id);
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || "Impossible de supprimer l'article.";
    } finally {
      loading.value = false;
    }
  }

  onMounted(loadArticles);

  return {
    loading,
    error,
    articles,
    search,
    filteredArticles,

    form,
    photoFile,
    photoPreview,
    isEditing,

    formatAr,
    onPhotoChange,
    resetForm,
    loadArticles,
    startCreate,
    startEdit,
    submit,
    removeArticle,
  };
}
