<script setup lang="ts">
import { computed, onMounted, ref, nextTick } from "vue";
import AppNavbar from "@/components/AppNavbar.vue";
import Modal from "bootstrap/js/dist/modal";
import { ChargeAPI, type Charge, type ChargeCategorie } from "@/services/charge";

const loading = ref(false);
const saving = ref(false);
const err = ref("");
const ok = ref("");

const items = ref<Charge[]>([]);
const categories = ref<ChargeCategorie[]>([]);

const filters = ref({
  q: "",
  categorie: "",
  statut: "",
  date_from: "",
  date_to: "",
});

const stats = ref<any>(null);

/* ===== Modal ===== */
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

onMounted(async () => {
  await nextTick();
  if (modalEl.value) modal = new Modal(modalEl.value, { backdrop: "static", keyboard: false });
  await load();
});
</script>

<template>
  <div class="zs-root">
    <AppNavbar />

    <div class="container-fluid py-4 zs-admin">
      <div class="zs-hero mb-3">
        <div class="d-flex align-items-start justify-content-between flex-wrap gap-2">
          <div class="min-width-0">
            <div class="d-flex align-items-center gap-2 flex-wrap">
              <div class="zs-dot"></div>
              <h4 class="mb-0 zs-title">Charges</h4>
              <span class="zs-pill-soft">
                <i class="fa-solid fa-coins me-1"></i> Dépenses & coûts
              </span>
            </div>
            <div class="text-muted small mt-1">Salaires livreur, carburant, emballage, commissions…</div>
          </div>

          <div class="d-flex gap-2 flex-wrap">
            <button class="btn btn-primary zs-btn" @click="openCreate">
              <i class="fa-solid fa-plus me-2"></i> Nouvelle charge
            </button>
            <button class="btn btn-outline-secondary zs-btn" @click="load" :disabled="loading">
              <i class="fa-solid fa-rotate me-2"></i> Actualiser
            </button>
          </div>
        </div>

        <div class="zs-kpis mt-3">
          <div class="zs-kpi">
            <div class="zs-kpi-icon"><i class="fa-solid fa-sack-dollar"></i></div>
            <div class="zs-kpi-body">
              <div class="zs-kpi-label">Total</div>
              <div class="zs-kpi-value">{{ totalMontant }}</div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="err" class="alert alert-danger py-2">{{ err }}</div>
      <div v-if="ok" class="alert alert-success py-2">{{ ok }}</div>

      <!-- Filters -->
      <div class="card shadow-sm zs-card mb-3">
        <div class="card-body">
          <div class="row g-2 align-items-end">
            <div class="col-12 col-md-4">
              <label class="form-label small mb-1">Recherche</label>
              <input v-model="filters.q" class="form-control" placeholder="libellé, description..." />
            </div>

            <div class="col-12 col-md-3">
              <label class="form-label small mb-1">Catégorie</label>
              <select v-model="filters.categorie" class="form-select">
                <option value="">Toutes</option>
                <option v-for="c in categories" :key="c.id" :value="String(c.id)">{{ c.nom }}</option>
              </select>
            </div>

            <div class="col-12 col-md-2">
              <label class="form-label small mb-1">Statut</label>
              <select v-model="filters.statut" class="form-select">
                <option value="">Tous</option>
                <option value="PAYEE">Payée</option>
                <option value="BROUILLON">Brouillon</option>
                <option value="ANNULEE">Annulée</option>
              </select>
            </div>

            <div class="col-6 col-md-1">
              <label class="form-label small mb-1">Du</label>
              <input v-model="filters.date_from" type="date" class="form-control" />
            </div>
            <div class="col-6 col-md-1">
              <label class="form-label small mb-1">Au</label>
              <input v-model="filters.date_to" type="date" class="form-control" />
            </div>

            <div class="col-12 col-md-1 d-grid">
              <button class="btn btn-outline-dark zs-btn" @click="load" :disabled="loading">
                <i class="fa-solid fa-filter"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Table -->
      <div class="card shadow-sm zs-card">
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Date</th>
                  <th>Catégorie</th>
                  <th>Libellé</th>
                  <th class="text-end">Montant</th>
                  <th>Statut</th>
                  <th>Mode</th>
                  <th>Commande</th>
                  <th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="8" class="text-center py-4 text-muted">Chargement...</td>
                </tr>
                <tr v-else-if="items.length === 0">
                  <td colspan="8" class="text-center py-4 text-muted">Aucune charge</td>
                </tr>
                <tr v-for="it in items" :key="it.id">
                  <td>{{ it.date_charge }}</td>
                  <td>{{ it.categorie_nom || it.categorie }}</td>
                  <td class="fw-semibold">{{ it.libelle }}</td>
                  <td class="text-end fw-bold">{{ Number(it.montant).toLocaleString() }}</td>
                  <td>
                    <span class="badge bg-success" v-if="it.statut === 'PAYEE'">Payée</span>
                    <span class="badge bg-secondary" v-else-if="it.statut === 'BROUILLON'">Brouillon</span>
                    <span class="badge bg-danger" v-else>Annulée</span>
                  </td>
                  <td>{{ it.mode_paiement }}</td>
                  <td>{{ it.commande ?? "—" }}</td>
                  <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary me-2" @click="openEdit(it)">
                      <i class="fa-solid fa-pen"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" @click="remove(it)">
                      <i class="fa-solid fa-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Modal -->
      <div class="modal fade" tabindex="-1" ref="modalEl">
        <div class="modal-dialog modal-dialog-centered modal-lg">
          <div class="modal-content zs-modal">
            <div class="modal-header">
              <div class="fw-bold">
                <i class="fa-solid fa-coins me-2 text-primary"></i>
                {{ editingId ? "Modifier une charge" : "Nouvelle charge" }}
              </div>
              <button type="button" class="btn-close" @click="modal?.hide()"></button>
            </div>

            <div class="modal-body">
              <div v-if="err" class="alert alert-danger py-2">{{ err }}</div>

              <div class="row g-2">
                <div class="col-12 col-md-4">
                  <label class="form-label">Date</label>
                  <input v-model="form.date_charge" type="date" class="form-control" />
                </div>

                <div class="col-12 col-md-4">
                  <label class="form-label">Catégorie</label>
                  <select v-model="form.categorie" class="form-select">
                    <option value="">—</option>
                    <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.nom }}</option>
                  </select>
                </div>

                <div class="col-12 col-md-4">
                  <label class="form-label">Statut</label>
                  <select v-model="form.statut" class="form-select">
                    <option value="PAYEE">Payée</option>
                    <option value="BROUILLON">Brouillon</option>
                    <option value="ANNULEE">Annulée</option>
                  </select>
                </div>

                <div class="col-12">
                  <label class="form-label">Libellé</label>
                  <input v-model="form.libelle" class="form-control" placeholder="Ex: Salaire livreur" />
                </div>

                <div class="col-12">
                  <label class="form-label">Description</label>
                  <textarea v-model="form.description" class="form-control" rows="3"></textarea>
                </div>

                <div class="col-12 col-md-4">
                  <label class="form-label">Montant</label>
                  <input v-model="form.montant" class="form-control" placeholder="Ex: 20000" />
                </div>

                <div class="col-12 col-md-4">
                  <label class="form-label">Mode paiement</label>
                  <select v-model="form.mode_paiement" class="form-select">
                    <option value="CASH">Cash</option>
                    <option value="MVOLA">MVola</option>
                    <option value="ORANGE_MONEY">Orange Money</option>
                    <option value="VISA">VISA</option>
                    <option value="AUTRE">Autre</option>
                  </select>
                </div>

                <div class="col-12 col-md-4">
                  <label class="form-label">Commande (optionnel)</label>
                  <input v-model="form.commande" class="form-control" placeholder="ID commande" />
                </div>

                <div class="col-12">
                  <label class="form-label">Pièce / reçu (optionnel)</label>
                  <input type="file" class="form-control" @change="onPickPiece" />
                </div>
              </div>
            </div>

            <div class="modal-footer">
              <button class="btn btn-outline-secondary zs-btn" @click="modal?.hide()" :disabled="saving">
                Annuler
              </button>
              <button class="btn btn-primary zs-btn" @click="save" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="fa-solid fa-floppy-disk me-2"></i>
                Enregistrer
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.zs-admin{
  background:
    radial-gradient(900px 360px at 10% 0%, rgba(13,110,253,.10), transparent 55%),
    radial-gradient(800px 320px at 90% 10%, rgba(25,135,84,.08), transparent 55%),
    transparent;
}
.zs-hero{
  border-radius: 18px;
  border: 1px solid rgba(0,0,0,.08);
  background: rgba(255,255,255,.72);
  backdrop-filter: blur(12px);
  box-shadow: 0 14px 34px rgba(0,0,0,.10);
  padding: 14px;
}
.zs-dot{
  width: 10px; height: 10px; border-radius: 999px;
  background: rgba(13,110,253,1);
  box-shadow: 0 0 0 5px rgba(13,110,253,.14);
}
.zs-title{ font-weight: 950; color: #0f172a; }
.zs-pill-soft{
  font-size: .78rem;
  font-weight: 900;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,.06);
  background: rgba(255,255,255,.65);
  color: rgba(15,23,42,.70);
}
.zs-card{
  border-radius: 18px;
  border: 1px solid rgba(0,0,0,.08);
  background: rgba(255,255,255,.72);
  backdrop-filter: blur(12px);
}
.zs-btn{ border-radius: 14px; font-weight: 800; }
.zs-modal{
  border-radius: 18px;
  border: 1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.92);
  backdrop-filter: blur(12px);
  box-shadow: 0 24px 60px rgba(0,0,0,.18);
  overflow: hidden;
}
.zs-kpis{ display:flex; gap: 12px; flex-wrap:wrap; }
.zs-kpi{
  flex: 0 0 auto;
  min-width: 220px;
  display:flex; gap: 10px; align-items:center;
  padding: 10px 12px;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,.06);
  background: rgba(255,255,255,.65);
}
.zs-kpi-icon{
  width: 42px; height: 42px; border-radius: 16px;
  display:flex; align-items:center; justify-content:center;
  border: 1px solid rgba(0,0,0,.06);
  background: rgba(255,255,255,.85);
}
.zs-kpi-label{ font-size: .78rem; font-weight: 900; color: rgba(15,23,42,.62); }
.zs-kpi-value{ font-weight: 950; font-size: 1.15rem; color: rgba(15,23,42,.88); }
</style>
