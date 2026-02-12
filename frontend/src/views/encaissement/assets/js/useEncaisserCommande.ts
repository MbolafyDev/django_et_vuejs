import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { EncaissementAPI, type EncaissementCommande, type ModePaiement } from "@/services/encaissement";

export function useEncaisserCommande() {
  const router = useRouter();
  const route = useRoute();

  const id = Number(route.params.id);

  const loading = ref(false);
  const submitting = ref(false);
  const commande = ref<EncaissementCommande | null>(null);

  const mode = ref<ModePaiement>("ESPECE");
  const reference = ref("");
  const note = ref("");

  const error = ref("");
  const errorRef = ref("");

  function money(v: number) {
    try {
      return new Intl.NumberFormat("fr-FR").format(v) + " Ar";
    } catch {
      return `${v} Ar`;
    }
  }

  function back() {
    router.push({ name: "encaissement_list" });
  }

  async function load() {
    loading.value = true;
    try {
      const res = await EncaissementAPI.getCommande(id);
      commande.value = res.data;

      if (commande.value?.paiement_statut !== "EN_ATTENTE") {
        back();
      }
    } finally {
      loading.value = false;
    }
  }

  async function submit() {
    error.value = "";
    errorRef.value = "";

    if (mode.value !== "ESPECE" && !reference.value.trim()) {
      errorRef.value = "Référence obligatoire pour Mobile Money.";
      return;
    }

    submitting.value = true;
    try {
      await EncaissementAPI.encaisserCommande(id, {
        mode: mode.value,
        reference: reference.value.trim() || undefined,
        note: note.value.trim() || undefined,
      });
      back();
    } catch (e: any) {
      error.value = e?.response?.data?.detail || JSON.stringify(e?.response?.data || e) || "Erreur encaissement";
    } finally {
      submitting.value = false;
    }
  }

  onMounted(load);

  return {
    id,
    loading,
    submitting,
    commande,
    mode,
    reference,
    note,
    error,
    errorRef,
    money,
    back,
    submit,
  };
}
