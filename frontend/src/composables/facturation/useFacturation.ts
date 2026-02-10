// src/composables/facturation/useFacturation.ts
import { ref, computed } from "vue";
import { FacturationAPI, type CommandeFacturationRow } from "@/services/facturation";
import { downloadBlob, openBlobInNewTab } from "@/utils/blob";

export function useFacturation() {
  const loading = ref(false);
  const error = ref("");

  const commandes = ref<CommandeFacturationRow[]>([]);
  const selectedIds = ref<number[]>([]);

  const loadingPdfId = ref<number | null>(null);
  const loadingBulkPdf = ref(false);

  const isAllSelected = computed(() => {
    return commandes.value.length > 0 && selectedIds.value.length === commandes.value.length;
  });

  function toggleAll(checked: boolean) {
    selectedIds.value = checked ? commandes.value.map((x) => x.id) : [];
  }

  async function load() {
    loading.value = true;
    error.value = "";
    try {
      const res = await FacturationAPI.list();
      commandes.value = res.data?.results ?? res.data;
      selectedIds.value = [];
    } catch (err: any) {
      error.value = err?.response?.data?.detail || "Erreur chargement commandes";
    } finally {
      loading.value = false;
    }
  }

  async function openPdf(id: number) {
    error.value = "";
    loadingPdfId.value = id;
    try {
      const res = await FacturationAPI.pdfInlineBlob(id);
      openBlobInNewTab(res.data, "application/pdf", 30_000);
    } catch (err: any) {
      error.value = err?.response?.data?.detail || "Erreur ouverture PDF";
    } finally {
      loadingPdfId.value = null;
    }
  }

  async function downloadPdf(id: number, numero: string) {
    error.value = "";
    loadingPdfId.value = id;
    try {
      const res = await FacturationAPI.pdfDownloadBlob(id);
      downloadBlob(res.data, `${(numero || "facture").replaceAll("/", "-")}.pdf`, "application/pdf");
    } catch (err: any) {
      error.value = err?.response?.data?.detail || "Erreur téléchargement PDF";
    } finally {
      loadingPdfId.value = null;
    }
  }

  async function downloadSelectedZip() {
    error.value = "";
    try {
      const res = await FacturationAPI.bulkDownload(selectedIds.value);
      downloadBlob(res.data, "factures_selection.zip", "application/zip");
    } catch (err: any) {
      error.value = err?.response?.data?.detail || "Erreur téléchargement ZIP sélection";
    }
  }

  async function downloadAll() {
    error.value = "";
    try {
      const res = await FacturationAPI.downloadAll();
      downloadBlob(res.data, "factures_toutes.zip", "application/zip");
    } catch (err: any) {
      error.value = err?.response?.data?.detail || "Erreur téléchargement ZIP";
    }
  }

  async function previewSelectedPdf() {
    if (selectedIds.value.length === 0) return;
    error.value = "";
    loadingBulkPdf.value = true;
    try {
      const res = await FacturationAPI.bulkPdfBlob(selectedIds.value, false);
      openBlobInNewTab(res.data, "application/pdf", 60_000);
    } catch (err: any) {
      error.value = err?.response?.data?.detail || "Erreur preview PDF sélection";
    } finally {
      loadingBulkPdf.value = false;
    }
  }

  async function downloadSelectedPdf() {
    if (selectedIds.value.length === 0) return;
    error.value = "";
    loadingBulkPdf.value = true;
    try {
      const res = await FacturationAPI.bulkPdfBlob(selectedIds.value, true);
      downloadBlob(res.data, "factures_selection.pdf", "application/pdf");
    } catch (err: any) {
      error.value = err?.response?.data?.detail || "Erreur téléchargement PDF sélection";
    } finally {
      loadingBulkPdf.value = false;
    }
  }

  return {
    loading,
    error,
    commandes,
    selectedIds,
    loadingPdfId,
    loadingBulkPdf,
    isAllSelected,
    toggleAll,
    load,
    openPdf,
    downloadPdf,
    downloadSelectedZip,
    downloadAll,
    previewSelectedPdf,
    downloadSelectedPdf,
  };
}
