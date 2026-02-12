import { computed, onMounted, ref, watch } from "vue";
import { LivraisonAPI, type FraisLivraison, type LieuLivraison, type LieuCategorie } from "@/services/livraison";
import { unwrapList } from "@/services/pagination";

export function useFraisLivraison() {
  const loading = ref(false);
  const error = ref("");

  const lieux = ref<LieuLivraison[]>([]);
  const fraisList = ref<FraisLivraison[]>([]);
  const search = ref("");

  const form = ref<{ id?: number; lieu: number | null; frais_override: number | null; note: string }>({
    lieu: null,
    frais_override: null,
    note: "",
  });

  const overrideEnabled = ref(false);
  const preview = ref<{ frais_calcule: number; frais_final: number } | null>(null);

  const isEditing = computed(() => !!form.value.id);

  const filteredFrais = computed(() => {
    const q = search.value.trim().toLowerCase();
    if (!q) return fraisList.value;
    return fraisList.value.filter((x) => (x.lieu_detail?.nom || "").toLowerCase().includes(q));
  });

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

  function formatAr(n: number) {
    return `${Math.round(n || 0).toLocaleString("fr-FR")} Ar`;
  }

  function resetForm() {
    form.value = { lieu: null, frais_override: null, note: "" };
    overrideEnabled.value = false;
    preview.value = null;
    error.value = "";
  }

  function startCreate() {
    resetForm();
  }

  function startEdit(x: FraisLivraison) {
    error.value = "";
    form.value = { id: x.id, lieu: x.lieu, frais_override: x.frais_override, note: x.note || "" };
    overrideEnabled.value = x.frais_override !== null;
  }

  async function loadFrais() {
    loading.value = true;
    error.value = "";
    try {
      const [r1, r2] = await Promise.all([
        LivraisonAPI.listLieux({ actif: 1 }),
        LivraisonAPI.listFrais(),
      ]);

      lieux.value = unwrapList<LieuLivraison>(r1.data);

      const raw = unwrapList<any>(r2.data);
      fraisList.value = raw.map((x) => ({
        ...x,
        frais_calcule: x.frais_calcule ?? x.frais_calculé ?? 0,
      }));
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || "Impossible de charger les frais.";
    } finally {
      loading.value = false;
    }
  }

  watch(overrideEnabled, (v) => {
    if (!v) form.value.frais_override = null;
  });

  // debounce preview + ignore anciennes requêtes
  let tPrev: any = null;
  let previewReqId = 0;

  watch(
    () => [form.value.lieu, overrideEnabled.value, form.value.frais_override] as const,
    () => {
      preview.value = null;
      if (!form.value.lieu) return;

      clearTimeout(tPrev);
      const current = ++previewReqId;

      tPrev = setTimeout(async () => {
        try {
          const res = await LivraisonAPI.calculer({
            lieu: form.value.lieu as number,
            frais_override: overrideEnabled.value ? form.value.frais_override : null,
          });

          if (current !== previewReqId) return;

          preview.value = {
            frais_calcule: res.data.frais_calcule ?? res.data.frais_calculé ?? 0,
            frais_final: res.data.frais_final ?? 0,
          };
        } catch {
          if (current !== previewReqId) return;
          preview.value = null;
        }
      }, 250);
    },
    { immediate: true }
  );

  async function submit() {
    error.value = "";
    if (!form.value.lieu) {
      error.value = "Le champ 'lieu' est obligatoire.";
      return;
    }

    loading.value = true;
    try {
      const payload = {
        lieu: form.value.lieu,
        frais_override: overrideEnabled.value ? form.value.frais_override : null,
        note: form.value.note,
      };

      if (!form.value.id) await LivraisonAPI.createFrais(payload);
      else await LivraisonAPI.updateFrais(form.value.id, payload);

      resetForm();
      await loadFrais();
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

  async function removeFrais(x: FraisLivraison) {
    const ok = confirm(`Supprimer le frais de "${x.lieu_detail?.nom}" ?`);
    if (!ok) return;

    loading.value = true;
    error.value = "";
    try {
      await LivraisonAPI.removeFrais(x.id);
      await loadFrais();
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || "Impossible de supprimer le frais.";
    } finally {
      loading.value = false;
    }
  }

  onMounted(loadFrais);

  return {
    loading, error,
    lieux, fraisList,
    search, filteredFrais,
    form, overrideEnabled, preview, isEditing,
    labelCat, formatAr,
    resetForm, startCreate, startEdit,
    loadFrais, submit, removeFrais,
  };
}
