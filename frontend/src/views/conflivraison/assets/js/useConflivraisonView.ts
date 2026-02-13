import { computed, onMounted, reactive, ref, nextTick, onBeforeUnmount } from "vue";
import Modal from "bootstrap/js/dist/modal"; // ✅ FIX (ne pas importer "bootstrap")
import {
  ConflivraisonAPI,
  type Livraison,
  type LivraisonStatut,
  type CommandeProgrammation,
} from "@/services/conflivraison";
import { api } from "@/services/api";

export function useConflivraisonView() {
  const loading = ref(false);
  const error = ref<string | null>(null);

  /** ✅ Commandes à programmer */
  const loadingCmd = ref(false);
  const commandes = ref<CommandeProgrammation[]>([]);
  const totalCmd = ref(0);
  const nextCmdUrl = ref<string | null>(null);
  const prevCmdUrl = ref<string | null>(null);
  const programmationDates = reactive<Record<number, string>>({});

  function toApiPath(url: string) {
    try {
      const u = new URL(url);
      const path = u.pathname + u.search;
      return path.startsWith("/api") ? path.replace("/api", "") : path;
    } catch {
      return (url || "").replace("/api", "");
    }
  }

  async function loadCommandes(url?: string) {
    loadingCmd.value = true;
    error.value = null;
    try {
      const res = url ? await api.get(toApiPath(url)) : await ConflivraisonAPI.listCommandes();
      const data: any = res.data;

      commandes.value = data.results || [];
      totalCmd.value = data.count || 0;
      nextCmdUrl.value = data.next || null;
      prevCmdUrl.value = data.previous || null;

      for (const c of commandes.value) {
        if (!programmationDates[c.id]) {
          programmationDates[c.id] = (c.date_livraison || c.date_prevue || "") as string;
        }
      }
    } catch (e: any) {
      error.value = e?.response?.data?.detail || "Erreur chargement commandes";
    } finally {
      loadingCmd.value = false;
    }
  }

  function nextCmd() {
    if (nextCmdUrl.value) loadCommandes(nextCmdUrl.value);
  }
  function prevCmd() {
    if (prevCmdUrl.value) loadCommandes(prevCmdUrl.value);
  }

  async function programmer(c: CommandeProgrammation) {
    const d = (programmationDates[c.id] || "").trim();
    if (!d) return;

    loading.value = true;
    error.value = null;
    try {
      await ConflivraisonAPI.programmerCommande(c.id, d);
      await refreshAll();
    } catch (e: any) {
      error.value = e?.response?.data?.detail || "Erreur programmation";
    } finally {
      loading.value = false;
    }
  }

  /** ✅ Livraisons */
  const items = ref<Livraison[]>([]);
  const total = ref(0);
  const nextUrl = ref<string | null>(null);
  const prevUrl = ref<string | null>(null);

  const filters = reactive({
    q: "",
    statut: "" as "" | LivraisonStatut,
    date_prevue: "",
  });

  const showFilters = ref(false);
  function toggleFilters() {
    showFilters.value = !showFilters.value;
  }

  const hasActiveFilters = computed(() => !!(filters.q.trim() || filters.statut || filters.date_prevue));

  function resetFilters() {
    filters.q = "";
    filters.statut = "";
    filters.date_prevue = "";
    load();
  }

  const paramsBase = () => {
    const p: any = {};
    if (filters.q.trim()) p.q = filters.q.trim();
    if (filters.statut) p.statut = filters.statut;
    if (filters.date_prevue) p.date_prevue = filters.date_prevue;
    return p;
  };

  async function load(url?: string) {
    loading.value = true;
    error.value = null;
    try {
      const res = url ? await api.get(toApiPath(url)) : await ConflivraisonAPI.list(paramsBase());
      const data: any = res.data;

      items.value = data.results || [];
      total.value = data.count || 0;
      nextUrl.value = data.next || null;
      prevUrl.value = data.previous || null;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || "Erreur chargement livraisons";
    } finally {
      loading.value = false;
    }
  }

  function applyFilters() {
    load();
  }
  function next() {
    if (nextUrl.value) load(nextUrl.value);
  }
  function prev() {
    if (prevUrl.value) load(prevUrl.value);
  }

  async function refreshAll() {
    await loadCommandes();
    await load();
  }

  async function sync() {
    loading.value = true;
    error.value = null;
    try {
      await ConflivraisonAPI.syncFromCommandes();
      await refreshAll();
    } catch (e: any) {
      error.value = e?.response?.data?.detail || "Erreur sync";
    } finally {
      loading.value = false;
    }
  }

  function isFinal(s: LivraisonStatut) {
    return s === "LIVREE" || s === "ANNULEE";
  }

  function labelStatut(s: LivraisonStatut) {
    const map: any = {
      A_PREPARER: "À préparer",
      EN_LIVRAISON: "En livraison",
      LIVREE: "Livrée",
      ANNULEE: "Annulée",
      REPORTEE: "Reportée",
    };
    return map[s] || s;
  }

  function statusClass(s: LivraisonStatut) {
    if (s === "LIVREE") return "zs-st zs-st-done";
    if (s === "ANNULEE") return "zs-st zs-st-cancel";
    if (s === "REPORTEE") return "zs-st zs-st-warn";
    if (s === "EN_LIVRAISON") return "zs-st zs-st-ship";
    return "zs-st zs-st-muted";
  }

  function statusIcon(s: LivraisonStatut) {
    if (s === "LIVREE") return "fa-circle-check";
    if (s === "ANNULEE") return "fa-ban";
    if (s === "REPORTEE") return "fa-calendar-days";
    if (s === "EN_LIVRAISON") return "fa-truck";
    return "fa-box";
  }

  function formatDT(dt: string) {
    try {
      return new Date(dt).toLocaleString();
    } catch {
      return dt;
    }
  }

  /** ====== Modals (FIX) ====== */
  const actionModalEl = ref<HTMLElement | null>(null);
  const historyModalEl = ref<HTMLElement | null>(null);

  let actionModal: Modal | null = null;
  let historyModal: Modal | null = null;

  const modalAction = ref<LivraisonStatut | null>(null);
  const modalTarget = ref<Livraison | null>(null);
  const historyTarget = ref<Livraison | null>(null);

  const actionPayload = reactive({
    raison: "",
    commentaire: "",
    date_prevue: "",
  });

  const modalTitle = computed(() => {
    if (!modalAction.value) return "";
    return modalAction.value === "ANNULEE"
      ? "Annuler la livraison"
      : modalAction.value === "REPORTEE"
      ? "Reporter la livraison"
      : "Action";
  });

  async function ensureModals() {
    await nextTick();
    if (actionModalEl.value && !actionModal) {
      actionModal = Modal.getOrCreateInstance(actionModalEl.value, {
        backdrop: true,
        keyboard: true,
        focus: true,
      });
    }
    if (historyModalEl.value && !historyModal) {
      historyModal = Modal.getOrCreateInstance(historyModalEl.value, {
        backdrop: true,
        keyboard: true,
        focus: true,
      });
    }
  }

  async function openModal(action: LivraisonStatut, l: Livraison) {
    if (action !== "ANNULEE" && action !== "REPORTEE") return;

    modalAction.value = action;
    modalTarget.value = l;

    actionPayload.raison = "";
    actionPayload.commentaire = "";
    actionPayload.date_prevue = l.date_prevue || "";

    await ensureModals();
    if (!actionModal) {
      error.value = "Modal Action introuvable (ref non monté).";
      return;
    }
    actionModal.show();
  }

  async function confirmModal() {
    if (!modalAction.value || !modalTarget.value) return;

    const id = modalTarget.value.id;

    const payload: any = {
      raison: actionPayload.raison || "",
      commentaire: actionPayload.commentaire || "",
    };
    if (modalAction.value === "REPORTEE") {
      payload.date_prevue = actionPayload.date_prevue || null;
    }

    loading.value = true;
    error.value = null;
    try {
      if (modalAction.value === "ANNULEE") {
        await ConflivraisonAPI.annuler(id, payload);
      } else {
        await ConflivraisonAPI.reporter(id, payload);
      }

      await ensureModals();
      actionModal?.hide();

      modalAction.value = null;
      modalTarget.value = null;

      await refreshAll();
    } catch (e: any) {
      const d = e?.response?.data;
      error.value = d?.detail || (typeof d === "string" ? d : null) || "Erreur action";
    } finally {
      loading.value = false;
    }
  }

  async function openHistory(l: Livraison) {
    loading.value = true;
    error.value = null;
    try {
      const res = await ConflivraisonAPI.history(l.id);
      historyTarget.value = res.data;

      await ensureModals();
      if (!historyModal) {
        error.value = "Modal Historique introuvable (ref non monté).";
        return;
      }
      historyModal.show();
    } catch (e: any) {
      const d = e?.response?.data;
      error.value = d?.detail || (typeof d === "string" ? d : null) || "Erreur chargement historique";
    } finally {
      loading.value = false;
    }
  }

  async function act(action: "EN_LIVRAISON" | "LIVREE", l: Livraison) {
    loading.value = true;
    error.value = null;
    try {
      if (action === "EN_LIVRAISON") await ConflivraisonAPI.setEnLivraison(l.id, {});
      if (action === "LIVREE") await ConflivraisonAPI.livrer(l.id, {});
      await refreshAll();
    } catch (e: any) {
      const d = e?.response?.data;
      error.value = d?.detail || (typeof d === "string" ? d : null) || "Erreur action";
    } finally {
      loading.value = false;
    }
  }

  onMounted(async () => {
    await refreshAll();
    await ensureModals(); // ✅ initialise aussi au montage
  });

  onBeforeUnmount(() => {
    actionModal?.dispose();
    historyModal?.dispose();
    actionModal = null;
    historyModal = null;
  });

  return {
    loading,
    error,

    loadingCmd,
    commandes,
    totalCmd,
    nextCmdUrl,
    prevCmdUrl,
    programmationDates,
    loadCommandes,
    nextCmd,
    prevCmd,
    programmer,

    items,
    total,
    nextUrl,
    prevUrl,
    filters,
    showFilters,
    hasActiveFilters,
    toggleFilters,
    resetFilters,
    load,
    applyFilters,
    next,
    prev,
    refreshAll,
    sync,

    isFinal,
    labelStatut,
    statusClass,
    statusIcon,
    formatDT,

    actionModalEl,
    historyModalEl,
    modalTitle,
    modalAction,
    actionPayload,
    historyTarget,
    openModal,
    confirmModal,
    act,
    openHistory,
  };
}
