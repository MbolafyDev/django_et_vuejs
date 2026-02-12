import { computed, onMounted, ref, nextTick } from "vue";
import Modal from "bootstrap/js/dist/modal";
import { ChargeAPI, type Charge, type ChargeCategorie } from "@/services/charge";

export function useChargesView() {
  const loading = ref(false);
  const saving = ref(false);
  const err = ref("");
  const ok = ref("");

  const items = ref<Charge[]>([]);
  const categories = ref<ChargeCategorie[]>([]);
  const stats = ref<any>(null);

  const filters = ref({
    q: "",
    categorie: "",
    statut: "",
    date_from: "",
    date_to: "",
  });

  // Modal
  const modalEl = ref<HTMLElement | null>(null);
  let modal: Modal | null = null;

  const editingId = ref<number | null>(null);

  const form = ref({
    date_charge: new Date().toISOString().slice(0, 10),
    categorie: "" as any,
    libelle: "",
    description: "",
    montant: "",
    statut: "PAYEE" as Charge["statut"],
    mode_paiement: "CASH" as Charge["mode_paiement"],
    commande: "" as any,
  });

  const pieceFile = ref<File | null>(null);

  function resetForm() {
    editingId.value = null;
    form.value = {
      date_charge: new Date().toISOString().slice(0, 10),
      categorie: "",
      libelle: "",
      description: "",
      montant: "",
      statut: "PAYEE",
      mode_paiement: "CASH",
      commande: "",
    };
    pieceFile.value = null;
    err.value = "";
    ok.value = "";
  }

  function openCreate() {
    resetForm();
    modal?.show();
  }

  function openEdit(item: Charge) {
    resetForm();
    editingId.value = item.id;
    form.value.date_charge = item.date_charge;
    form.value.categorie = item.categorie as any;
    form.value.libelle = item.libelle;
    form.value.description = item.description || "";
    form.value.montant = String(item.montant ?? "");
    form.value.statut = item.statut;
    form.value.mode_paiement = item.mode_paiement;
    form.value.commande = (item.commande ?? "") as any;
    modal?.show();
  }

  function onPickPiece(e: Event) {
    pieceFile.value = (e.target as HTMLInputElement).files?.[0] || null;
  }

  async function load() {
    loading.value = true;
    err.value = "";
    ok.value = "";
    try {
      const [catRes, res, st] = await Promise.all([
        ChargeAPI.listCategories({ actif: true, page_size: 200 }).catch(() => ({ data: { results: [] } })),
        ChargeAPI.listCharges({ ...filters.value, page_size: 200 }),
        ChargeAPI.stats({ ...filters.value }).catch(() => ({ data: null })),
      ]);

      categories.value = catRes.data?.results || catRes.data || [];
      items.value = res.data?.results || res.data || [];
      stats.value = st.data;
    } catch (e: any) {
      err.value = "Erreur chargement charges.";
    } finally {
      loading.value = false;
    }
  }

  async function save() {
    saving.value = true;
    err.value = "";
    ok.value = "";
    try {
      const payload: any = {
        date_charge: form.value.date_charge,
        categorie: Number(form.value.categorie),
        libelle: form.value.libelle,
        description: form.value.description,
        montant: form.value.montant,
        statut: form.value.statut,
        mode_paiement: form.value.mode_paiement,
        commande: form.value.commande ? Number(form.value.commande) : null,
        piece: pieceFile.value,
      };

      if (!payload.categorie) throw new Error("Catégorie requise");
      if (!payload.libelle) throw new Error("Libellé requis");
      if (!payload.montant) throw new Error("Montant requis");

      if (editingId.value) {
        await ChargeAPI.updateCharge(editingId.value, payload);
        ok.value = "Charge mise à jour ✅";
      } else {
        await ChargeAPI.createCharge(payload);
        ok.value = "Charge ajoutée ✅";
      }

      modal?.hide();
      await load();
    } catch (e: any) {
      err.value = e?.message || "Erreur enregistrement charge.";
    } finally {
      saving.value = false;
    }
  }

  async function remove(item: Charge) {
    if (!confirm(`Supprimer la charge: ${item.libelle} ?`)) return;
    try {
      await ChargeAPI.deleteCharge(item.id);
      await load();
    } catch (e) {
      alert("Erreur suppression.");
    }
  }

  const totalMontant = computed(() => {
    const s = stats.value?.total;
    return typeof s === "number" ? s.toLocaleString() : "0";
  });

  async function initModal() {
    await nextTick();
    if (modalEl.value) modal = new Modal(modalEl.value, { backdrop: "static", keyboard: false });
  }

  onMounted(async () => {
    await initModal();
    await load();
  });

  return {
    loading,
    saving,
    err,
    ok,
    items,
    categories,
    filters,
    stats,

    modalEl,
    editingId,
    form,
    pieceFile,

    totalMontant,

    resetForm,
    openCreate,
    openEdit,
    onPickPiece,
    load,
    save,
    remove,
  };
}
