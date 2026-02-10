<!-- FraisLivraisonView.vue -->
<template>
  <div class="zs-root">
    <AppNavbar />

    <div class="container-fluid py-4 zs-admin">
      <!-- HERO -->
      <div class="zs-hero mb-3">
        <div class="d-flex align-items-start justify-content-between flex-wrap gap-3">
          <div class="min-width-0">
            <div class="d-flex align-items-center gap-2 flex-wrap">
              <div class="zs-dot"></div>
              <h4 class="mb-0 zs-title">Frais de livraison</h4>
              <span class="zs-pill-soft">
                <i class="fa-solid fa-truck-fast me-1"></i> Calcul auto + override
              </span>
            </div>

            <div class="text-muted small mt-1">
              Paramètres • calcul automatique • modification manuelle • aperçu instantané
            </div>

            <!-- KPIs -->
            <div class="zs-kpis mt-3">
              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-list-check"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Résultats</div>
                  <div class="zs-kpi-value">{{ filteredFrais.length }}</div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-location-dot"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Lieux actifs</div>
                  <div class="zs-kpi-value">{{ lieux.length }}</div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-magnifying-glass"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Recherche</div>
                  <div class="zs-kpi-value">
                    <span v-if="search.trim()" class="text-primary fw-bold">ON</span>
                    <span v-else class="text-muted">OFF</span>
                  </div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-gear"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Mode</div>
                  <div class="zs-kpi-value">
                    <span v-if="isEditing" class="text-warning fw-bold">EDIT</span>
                    <span v-else class="text-success fw-bold">NEW</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="d-flex gap-2 flex-wrap align-items-center">
            <div class="zs-search">
              <i class="fa-solid fa-magnifying-glass"></i>
              <input v-model="search" type="text" class="zs-search-input" placeholder="Rechercher (lieu)" />
              <button v-if="search.trim()" class="zs-search-clear" @click="search = ''" title="Effacer">
                <i class="fa-solid fa-xmark"></i>
              </button>
            </div>

            <button class="btn btn-primary zs-btn zs-btn-neo" @click="startCreate" title="Nouveau">
              <i class="fa-solid fa-plus"></i>
              <span class="ms-2 d-none d-sm-inline">Nouveau</span>
            </button>

            <button class="btn btn-outline-secondary zs-btn zs-btn-neo" :disabled="loading" @click="loadFrais" title="Rafraîchir">
              <i class="fa-solid fa-rotate"></i>
              <span class="ms-2 d-none d-sm-inline">Rafraîchir</span>
            </button>
          </div>
        </div>
      </div>

      <!-- ERROR -->
      <div v-if="error" class="alert alert-danger py-2">
        <i class="fa-solid fa-triangle-exclamation me-2"></i>{{ error }}
      </div>

      <div class="row g-3">
        <!-- FORM PANEL -->
        <div class="col-12 col-lg-4">
          <div class="zs-panel">
            <div class="zs-panel-head d-flex align-items-center justify-content-between">
              <div class="fw-bold">
                <i class="fa-solid fa-truck-fast me-2 text-primary"></i>
                {{ isEditing ? "Modifier frais" : "Nouveau frais" }}
              </div>

              <button v-if="isEditing" class="btn btn-sm btn-outline-secondary zs-btn zs-btn-neo" @click="resetForm">
                <i class="fa-solid fa-xmark me-1"></i> Annuler
              </button>
            </div>

            <div class="zs-panel-body">
              <div class="mb-2">
                <label class="form-label small text-muted mb-1">Lieu *</label>
                <select v-model.number="form.lieu" class="form-select form-select-sm zs-input" :disabled="loading">
                  <option :value="null">-- Choisir --</option>
                  <option v-for="l in lieux" :key="l.id" :value="l.id">
                    {{ l.nom }} ({{ labelCat(l.categorie) }})
                  </option>
                </select>
              </div>

              <div class="d-flex align-items-center justify-content-between mt-2 mb-2">
                <div class="form-check m-0">
                  <input class="form-check-input" type="checkbox" v-model="overrideEnabled" id="overrideEnabled" />
                  <label class="form-check-label" for="overrideEnabled">
                    Modifier manuellement
                  </label>
                </div>

                <span class="zs-pill-soft">
                  <i class="fa-solid fa-wand-magic-sparkles me-1"></i>
                  Auto
                  <span class="ms-1 fw-bold" :class="overrideEnabled ? 'text-danger' : 'text-success'">
                    {{ overrideEnabled ? "OFF" : "ON" }}
                  </span>
                </span>
              </div>

              <div class="mb-2">
                <label class="form-label small text-muted mb-1">Frais override (Ar)</label>
                <input
                  v-model.number="form.frais_override"
                  type="number"
                  step="1"
                  class="form-control form-control-sm zs-input"
                  :disabled="loading || !overrideEnabled"
                  placeholder="Ex: 4500"
                />
              </div>

              <div class="mb-2">
                <label class="form-label small text-muted mb-1">Note</label>
                <input v-model="form.note" class="form-control form-control-sm zs-input" :disabled="loading" />
              </div>

              <div v-if="preview" class="zs-preview mt-2">
                <div class="zs-preview-row">
                  <span class="text-muted small">Calculé</span>
                  <span class="fw-bold">{{ formatAr(preview.frais_calcule) }}</span>
                </div>
                <div class="zs-preview-row">
                  <span class="text-muted small">Final</span>
                  <span class="fw-bold text-primary">{{ formatAr(preview.frais_final) }}</span>
                </div>
              </div>

              <div class="d-grid mt-3">
                <button class="btn btn-primary zs-btn zs-btn-neo" :disabled="loading" @click="submit">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="fa-solid fa-floppy-disk me-2"></i>
                  {{ isEditing ? "Enregistrer" : "Créer" }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- LIST PANEL -->
        <div class="col-12 col-lg-8">
          <div class="zs-panel">
            <div class="zs-panel-head d-flex align-items-center justify-content-between flex-wrap gap-2">
              <div class="d-flex align-items-center gap-2 min-width-0">
                <i class="fa-solid fa-list me-1 text-primary"></i>
                <span class="fw-bold">Liste</span>
                <span class="zs-pill-count">{{ filteredFrais.length }}</span>
              </div>

              <div class="text-muted small">
                {{ search.trim() ? `Filtré par: "${search}"` : "Tous les frais" }}
              </div>
            </div>

            <div class="zs-panel-body p-0">
              <div v-if="loading" class="p-3 text-muted">
                <span class="spinner-border spinner-border-sm me-2"></span>Chargement...
              </div>

              <div v-else-if="filteredFrais.length === 0" class="p-4 text-center text-muted">
                <i class="fa-solid fa-circle-info me-1"></i> Aucun frais.
              </div>

              <div v-else class="table-responsive zs-table-wrap">
                <table class="table table-sm align-middle mb-0 zs-table">
                  <thead>
                    <tr>
                      <th>Lieu</th>
                      <th class="text-end">Calculé</th>
                      <th class="text-end">Override</th>
                      <th class="text-end">Final</th>
                      <th class="text-end" style="width: 170px;">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="x in filteredFrais" :key="x.id">
                      <td class="fw-semibold">
                        <div class="d-flex flex-column">
                          <span>{{ x.lieu_detail?.nom }}</span>
                          <span class="text-muted small">{{ labelCat(x.lieu_detail?.categorie as any) }}</span>
                        </div>
                      </td>
                      <td class="text-end">{{ formatAr(x.frais_calcule) }}</td>
                      <td class="text-end">
                        <span
                          class="zs-pill-soft"
                          :class="x.frais_override === null ? 'zs-pill-muted' : 'zs-pill-warn'"
                        >
                          {{ x.frais_override === null ? "—" : formatAr(x.frais_override) }}
                        </span>
                      </td>
                      <td class="text-end fw-bold">{{ formatAr(x.frais_final) }}</td>
                      <td class="text-end">
                        <button class="btn btn-sm btn-outline-primary zs-btn zs-btn-neo me-2" @click="startEdit(x)" title="Modifier">
                          <i class="fa-solid fa-pen"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger zs-btn zs-btn-neo" @click="removeFrais(x)" title="Supprimer">
                          <i class="fa-solid fa-trash"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, watch } from "vue";
import AppNavbar from "@/components/AppNavbar.vue";
import { LivraisonAPI, type FraisLivraison, type LieuLivraison, type LieuCategorie } from "@/services/livraison";
import { unwrapList } from "@/services/pagination";

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
  return map[c] || c;
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
</script>

<style scoped>
.min-width-0{ min-width:0; }

/* Search “zs” */
.zs-search{
  display:flex; align-items:center; gap:.5rem;
  padding: .55rem .75rem;
  border-radius: 14px;
  background: rgba(255,255,255,.9);
  border: 1px solid rgba(0,0,0,.06);
  box-shadow: 0 10px 24px rgba(0,0,0,.06);
}
.zs-search i{ opacity:.65; }
.zs-search-input{
  border:0; outline:0; background:transparent;
  min-width: 220px;
}
.zs-search-clear{
  border:0; background:transparent; opacity:.7;
}
.zs-search-clear:hover{ opacity:1; }

/* Pills */
.zs-pill-muted{ opacity:.75; }
.zs-pill-warn{ background: rgba(255,193,7,.16); border: 1px solid rgba(255,193,7,.26); }

/* Table look (premium) */
.zs-table-wrap{ border-radius: 16px; overflow:hidden; }
.zs-table thead th{
  background: rgba(248,249,250,1);
  font-weight: 700;
  color: rgba(33,37,41,.75);
  border-bottom: 1px solid rgba(0,0,0,.06);
}
.zs-table tbody tr:hover{ background: rgba(13,110,253,.04); }
.zs-table td, .zs-table th{ padding: .85rem .9rem; }
.zs-input{ border-radius: 12px; }

.zs-preview{
  border-radius: 14px;
  border: 1px dashed rgba(13,110,253,.35);
  background: rgba(13,110,253,.06);
  padding: .75rem .85rem;
}
.zs-preview-row{
  display:flex; justify-content:space-between; align-items:center;
}
</style>
