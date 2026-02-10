<!-- LieuxLivraisonView.vue -->
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
              <h4 class="mb-0 zs-title">Lieux de livraison</h4>
              <span class="zs-pill-soft">
                <i class="fa-solid fa-location-dot me-1"></i> Zones & Catégories
              </span>
            </div>

            <div class="text-muted small mt-1">
              Paramètres • création • édition • activation • frais par défaut
            </div>

            <!-- KPIs -->
            <div class="zs-kpis mt-3">
              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-list-check"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Résultats</div>
                  <div class="zs-kpi-value">{{ filteredLieux.length }}</div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-circle-check"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Actifs</div>
                  <div class="zs-kpi-value">{{ actifsCount }}</div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-circle-xmark"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Inactifs</div>
                  <div class="zs-kpi-value">{{ inactifsCount }}</div>
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
            </div>
          </div>

          <!-- Actions -->
          <div class="d-flex gap-2 flex-wrap align-items-center">
            <div class="zs-search">
              <i class="fa-solid fa-magnifying-glass"></i>
              <input v-model="search" type="text" class="zs-search-input" placeholder="Rechercher (nom)" />
              <button v-if="search.trim()" class="zs-search-clear" @click="search = ''" title="Effacer">
                <i class="fa-solid fa-xmark"></i>
              </button>
            </div>

            <button class="btn btn-primary zs-btn zs-btn-neo" @click="startCreate" title="Nouveau">
              <i class="fa-solid fa-plus"></i>
              <span class="ms-2 d-none d-sm-inline">Nouveau</span>
            </button>

            <button class="btn btn-outline-secondary zs-btn zs-btn-neo" :disabled="loading" @click="loadLieux" title="Rafraîchir">
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
                <i class="fa-solid fa-location-dot me-2 text-primary"></i>
                {{ isEditing ? "Modifier lieu" : "Nouveau lieu" }}
              </div>

              <button v-if="isEditing" class="btn btn-sm btn-outline-secondary zs-btn zs-btn-neo" @click="resetForm">
                <i class="fa-solid fa-xmark me-1"></i> Annuler
              </button>
            </div>

            <div class="zs-panel-body">
              <div class="mb-2">
                <label class="form-label small text-muted mb-1">Nom *</label>
                <input v-model="form.nom" class="form-control form-control-sm zs-input" :disabled="loading" />
              </div>

              <div class="mb-2">
                <label class="form-label small text-muted mb-1">Catégorie *</label>
                <select v-model="form.categorie" class="form-select form-select-sm zs-input" :disabled="loading">
                  <option value="VILLE">Ville (3000Ar)</option>
                  <option value="PERIPHERIE">Périphérie (4000Ar)</option>
                  <option value="PLUS_PERIPHERIE">Plus périphérie (5000Ar)</option>
                  <option value="PROVINCE">Province (3000Ar)</option>
                  <option value="AUTRE">Autre (manuel)</option>
                </select>
              </div>

              <div class="d-flex align-items-center justify-content-between mt-2">
                <div class="form-check m-0">
                  <input class="form-check-input" type="checkbox" v-model="form.actif" id="lieuActif" />
                  <label class="form-check-label" for="lieuActif">Actif</label>
                </div>

                <span class="zs-pill-soft" :class="form.actif ? 'zs-pill-ok' : 'zs-pill-muted'">
                  <i class="fa-solid fa-circle me-1"></i>
                  {{ form.actif ? "Actif" : "Inactif" }}
                </span>
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
                <span class="zs-pill-count">{{ filteredLieux.length }}</span>
              </div>

              <div class="text-muted small">
                {{ search.trim() ? `Filtré par: "${search}"` : "Tous les lieux" }}
              </div>
            </div>

            <div class="zs-panel-body p-0">
              <div v-if="loading" class="p-3 text-muted">
                <span class="spinner-border spinner-border-sm me-2"></span>Chargement...
              </div>

              <div v-else-if="filteredLieux.length === 0" class="p-4 text-center text-muted">
                <i class="fa-solid fa-circle-info me-1"></i> Aucun lieu.
              </div>

              <div v-else class="table-responsive zs-table-wrap">
                <table class="table table-sm align-middle mb-0 zs-table">
                  <thead>
                    <tr>
                      <th>Nom</th>
                      <th>Catégorie</th>
                      <th class="text-end">Frais défaut</th>
                      <th class="text-end" style="width: 170px;">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="l in filteredLieux" :key="l.id">
                      <td class="fw-semibold">
                        <div class="d-flex align-items-center gap-2">
                          <span>{{ l.nom }}</span>
                          <span v-if="!l.actif" class="badge text-bg-secondary">Inactif</span>
                          <span v-else class="badge text-bg-success">Actif</span>
                        </div>
                      </td>
                      <td class="text-muted">{{ labelCat(l.categorie) }}</td>
                      <td class="text-end fw-bold">{{ formatAr(l.default_frais) }}</td>
                      <td class="text-end">
                        <button class="btn btn-sm btn-outline-primary zs-btn zs-btn-neo me-2" @click="startEdit(l)" title="Modifier">
                          <i class="fa-solid fa-pen"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger zs-btn zs-btn-neo" @click="removeLieu(l)" title="Supprimer">
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
import { onMounted, ref, computed } from "vue";
import AppNavbar from "@/components/AppNavbar.vue";
import { LivraisonAPI, type LieuLivraison, type LieuCategorie } from "@/services/livraison";
import { unwrapList } from "@/services/pagination";

const loading = ref(false);
const error = ref("");
const lieux = ref<LieuLivraison[]>([]);
const search = ref("");

const filteredLieux = computed(() => {
  const q = search.value.trim().toLowerCase();
  if (!q) return lieux.value;
  return lieux.value.filter((x) => (x.nom || "").toLowerCase().includes(q));
});

const actifsCount = computed(() => filteredLieux.value.filter((x) => x.actif).length);
const inactifsCount = computed(() => filteredLieux.value.filter((x) => !x.actif).length);

const form = ref<{ id?: number; nom: string; categorie: LieuCategorie; actif: boolean }>({
  nom: "",
  categorie: "VILLE",
  actif: true,
});

const isEditing = computed(() => !!form.value.id);

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

function formatAr(value: number) {
  return `${Math.round(value || 0).toLocaleString("fr-FR")} Ar`;
}

function resetForm() {
  form.value = { nom: "", categorie: "VILLE", actif: true };
  error.value = "";
}

function startCreate() {
  resetForm();
}

function startEdit(l: LieuLivraison) {
  error.value = "";
  form.value = { id: l.id, nom: l.nom, categorie: l.categorie, actif: l.actif };
}

async function loadLieux() {
  loading.value = true;
  error.value = "";
  try {
    const res = await LivraisonAPI.listLieux();
    lieux.value = unwrapList<LieuLivraison>(res.data);
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || "Impossible de charger les lieux.";
  } finally {
    loading.value = false;
  }
}

async function submit() {
  error.value = "";
  if (!form.value.nom.trim()) {
    error.value = "Le champ 'nom' est obligatoire.";
    return;
  }

  loading.value = true;
  try {
    const payload = { nom: form.value.nom.trim(), categorie: form.value.categorie, actif: form.value.actif };

    if (!form.value.id) await LivraisonAPI.createLieu(payload);
    else await LivraisonAPI.updateLieu(form.value.id, payload);

    resetForm();
    await loadLieux();
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

async function removeLieu(l: LieuLivraison) {
  const ok = confirm(`Supprimer le lieu "${l.nom}" ?`);
  if (!ok) return;

  loading.value = true;
  error.value = "";
  try {
    await LivraisonAPI.removeLieu(l.id);
    await loadLieux();
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || "Impossible de supprimer le lieu.";
  } finally {
    loading.value = false;
  }
}

onMounted(loadLieux);
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
.zs-pill-ok{ background: rgba(25,135,84,.14); border: 1px solid rgba(25,135,84,.22); }
.zs-pill-muted{ opacity:.75; }

/* Table look */
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
</style>
