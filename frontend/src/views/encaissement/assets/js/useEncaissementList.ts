import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { EncaissementAPI, type EncaissementCommande } from "@/services/encaissement";

export function useEncaissementList() {
  const router = useRouter();

  const loading = ref(false);
  const rows = ref<EncaissementCommande[]>([]);
  const count = ref(0);

  const paiement_statut = ref<string>("");
  const q = ref<string>("");

  const page = ref(1);
  const pageSize = ref(20);

  const showFilters = ref(false);
  const viewMode = ref<"table" | "card">("table");

  const noop = () => {};

  const hasActiveFilters = computed(() => !!(paiement_statut.value || q.value.trim()));
  const hasNext = computed(() => page.value * pageSize.value < count.value);

  function toggleFilters() {
    showFilters.value = !showFilters.value;
  }

  function money(v: number) {
    try {
      return new Intl.NumberFormat("fr-FR").format(v) + " Ar";
    } catch {
      return `${v} Ar`;
    }
  }

  function paiementLabel(s: any) {
    if (s === "PAYEE") return "Payée";
    if (s === "ANNULEE") return "Annulée";
    return "En attente";
  }

  function paiementClass(s: any) {
    if (s === "PAYEE") return "zs-st zs-st-done";
    if (s === "ANNULEE") return "zs-st zs-st-neutral";
    return "zs-st zs-st-ship";
  }

  function paiementIcon(s: any) {
    if (s === "PAYEE") return "fa-circle-check";
    if (s === "ANNULEE") return "fa-circle-xmark";
    return "fa-hourglass-half";
  }

  function goEncaisser(id: number) {
    router.push({ name: "encaissement_encaisser", params: { id } });
  }

  function goPending() {
    paiement_statut.value = "EN_ATTENTE";
    page.value = 1;
    load();
  }

  function resetFilters() {
    paiement_statut.value = "";
    q.value = "";
    page.value = 1;
    load();
  }

  function applyFilters() {
    page.value = 1;
    load();
  }

  function nextPage() {
    if (!hasNext.value) return;
    page.value += 1;
    load();
  }

  function prevPage() {
    if (page.value <= 1) return;
    page.value -= 1;
    load();
  }

  function onPageSizeChange() {
    page.value = 1;
    load();
  }

  async function annuler(id: number) {
    if (!confirm("Annuler le paiement de cette commande ?")) return;
    loading.value = true;
    try {
      await EncaissementAPI.annulerPaiement(id, { note: "Annulation depuis l'écran encaissement." });
      await load();
    } finally {
      loading.value = false;
    }
  }

  async function load() {
    loading.value = true;
    try {
      const params: any = {
        paiement_statut: paiement_statut.value || undefined,
        q: q.value || undefined,
        page: page.value,
        page_size: pageSize.value,
      };

      const res = await EncaissementAPI.listCommandes(params);
      const data = res.data as any;

      rows.value = data.results || [];
      count.value = data.count || 0;
    } finally {
      loading.value = false;
    }
  }

  onMounted(load);

  return {
    loading,
    rows,
    count,

    paiement_statut,
    q,

    page,
    pageSize,

    showFilters,
    viewMode,

    hasActiveFilters,
    hasNext,

    money,
    paiementLabel,
    paiementClass,
    paiementIcon,

    toggleFilters,
    resetFilters,
    applyFilters,
    nextPage,
    prevPage,
    onPageSizeChange,
    goEncaisser,
    goPending,
    annuler,
    load,

    noop,
  };
}
