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
              <h4 class="mb-0 zs-title">Achats</h4>
              <span class="zs-pill-soft">
                <i class="fa-solid fa-cart-shopping me-1"></i> Stock & Historique
              </span>
            </div>

            <div class="text-muted small mt-1">
              Gestion des achats • mise à jour du stock • lignes d’articles
            </div>

            <!-- KPIs -->
            <div class="zs-kpis mt-3">
              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-receipt"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Achats</div>
                  <div class="zs-kpi-value">{{ achats.length }}</div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-boxes-stacked"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Articles</div>
                  <div class="zs-kpi-value">{{ articles.length }}</div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-magnifying-glass"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Filtre</div>
                  <div class="zs-kpi-value">
                    <span v-if="search.trim()" class="text-primary fw-bold">ON</span>
                    <span v-else class="text-muted">OFF</span>
                  </div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-gauge-high"></i></div>
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
          <div class="d-flex align-items-center gap-2 flex-wrap">
            <div class="zs-search">
              <i class="fa-solid fa-magnifying-glass"></i>
              <input
                v-model="search"
                type="text"
                class="form-control form-control-sm zs-input zs-search-input"
                placeholder="Rechercher (fournisseur)"
              />
            </div>

            <button class="btn btn-primary zs-btn zs-btn-neo" @click="startCreate">
              <i class="fa-solid fa-plus"></i>
              <span class="ms-2 d-none d-sm-inline">Nouveau</span>
            </button>

            <button class="btn btn-outline-secondary zs-btn zs-btn-neo" :disabled="loading" @click="loadAll" title="Rafraîchir">
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
        <div class="col-12 col-lg-5">
          <div class="zs-panel">
            <div class="zs-panel-head d-flex align-items-center justify-content-between flex-wrap gap-2">
              <div class="d-flex align-items-center gap-2 min-width-0">
                <i class="fa-solid fa-cart-shopping me-1 text-primary"></i>
                <span class="fw-bold">{{ isEditing ? "Modifier achat" : "Nouvel achat" }}</span>
                <span class="zs-pill-count">{{ form.lignes.length }}</span>
              </div>

              <button v-if="isEditing" class="btn btn-sm btn-outline-secondary zs-btn zs-btn-neo" @click="resetForm">
                Annuler
              </button>
            </div>

            <div class="zs-panel-body">
              <div class="row g-2">
                <div class="col-12">
                  <label class="form-label small text-muted mb-1">Fournisseur</label>
                  <input v-model="form.fournisseur" class="form-control form-control-sm zs-input" :disabled="loading" />
                </div>

                <div class="col-12 col-md-6">
                  <label class="form-label small text-muted mb-1">Date</label>
                  <input v-model="form.date_achat" type="date" class="form-control form-control-sm zs-input" :disabled="loading" />
                </div>

                <div class="col-12">
                  <label class="form-label small text-muted mb-1">Note</label>
                  <textarea v-model="form.note" class="form-control form-control-sm zs-input" rows="2" :disabled="loading"></textarea>
                </div>
              </div>

              <div class="d-flex align-items-center justify-content-between mt-3 mb-2">
                <div class="fw-semibold">
                  <i class="fa-solid fa-layer-group me-2 text-primary"></i>Lignes
                </div>
                <button class="btn btn-sm btn-outline-primary zs-btn zs-btn-neo" @click="addLine" :disabled="loading">
                  <i class="fa-solid fa-plus me-1"></i> Ajouter ligne
                </button>
              </div>

              <div v-if="form.lignes.length === 0" class="zs-empty">
                Ajoute au moins une ligne (article + quantité).
              </div>

              <!-- LINES -->
              <div
                v-for="(l, idx) in form.lignes"
                :key="idx"
                class="zs-line-card"
              >
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <div class="fw-semibold">
                    <i class="fa-solid fa-tag me-2 text-primary"></i>
                    Ligne {{ idx + 1 }}
                  </div>
                  <button class="btn btn-sm btn-outline-danger zs-btn zs-btn-neo" @click="removeLine(idx)" :disabled="loading">
                    <i class="fa-solid fa-trash"></i>
                  </button>
                </div>

                <div class="mb-2">
                  <label class="form-label small text-muted mb-1">Article *</label>
                  <select v-model.number="l.article" class="form-select form-select-sm zs-input" :disabled="loading">
                    <option :value="null">-- Choisir --</option>
                    <option v-for="a in articles" :key="a.id" :value="a.id">
                      {{ a.nom_produit }} ({{ a.reference }}) | Stock: {{ a.quantite_stock }}
                    </option>
                  </select>
                </div>

                <div class="row g-2">
                  <div class="col-4">
                    <label class="form-label small text-muted mb-1">Qté *</label>
                    <input v-model.number="l.quantite" type="number" min="1" class="form-control form-control-sm zs-input" :disabled="loading" />
                  </div>
                  <div class="col-4">
                    <label class="form-label small text-muted mb-1">P. achat</label>
                    <input v-model="l.prix_achat_unitaire" type="number" step="1" class="form-control form-control-sm zs-input" :disabled="loading" />
                  </div>
                  <div class="col-4">
                    <label class="form-label small text-muted mb-1">P. vente</label>
                    <input v-model="l.prix_vente_unitaire" type="number" step="1" class="form-control form-control-sm zs-input" :disabled="loading" />
                  </div>
                </div>

                <div class="form-check mt-2">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    v-model="l.maj_prix_article"
                    :disabled="loading"
                    :id="`majPrix-${idx}`"
                  />
                  <label class="form-check-label small" :for="`majPrix-${idx}`">
                    Mettre à jour le prix de l’article
                  </label>
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
        <div class="col-12 col-lg-7">
          <div class="zs-panel">
            <div class="zs-panel-head d-flex align-items-center justify-content-between flex-wrap gap-2">
              <div class="d-flex align-items-center gap-2 min-width-0">
                <i class="fa-solid fa-clock-rotate-left me-1 text-primary"></i>
                <span class="fw-bold">Historique</span>
                <span class="zs-pill-count">{{ filtered.length }}</span>
              </div>
              <div class="text-muted small">
                Recherche par fournisseur
              </div>
            </div>

            <div class="zs-panel-body p-0">
              <div v-if="loading" class="p-3 text-muted">
                <span class="spinner-border spinner-border-sm me-2"></span>Chargement...
              </div>

              <div v-else-if="filtered.length === 0" class="p-4 text-center text-muted">
                <i class="fa-solid fa-circle-info me-1"></i> Aucun achat.
              </div>

              <div v-else class="table-responsive zs-table-wrap">
                <table class="table table-sm align-middle mb-0 zs-table">
                  <thead>
                    <tr>
                      <th style="width:90px;">#</th>
                      <th>Fournisseur</th>
                      <th style="width:150px;">Date</th>
                      <th class="text-end" style="width:160px;">Total</th>
                      <th class="text-end" style="width:190px;">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="a in filtered" :key="a.id">
                      <td class="fw-bold">#{{ a.id }}</td>
                      <td class="zs-ellipsis2">{{ a.fournisseur || "—" }}</td>
                      <td class="text-muted">{{ a.date_achat || "—" }}</td>
                      <td class="text-end fw-bold">{{ formatAr(a.total || 0) }}</td>
                      <td class="text-end">
                        <div class="d-inline-flex gap-2">
                          <button class="btn btn-sm btn-outline-primary zs-btn zs-btn-neo" @click="startEdit(a)">
                            <i class="fa-solid fa-pen"></i>
                          </button>
                          <button class="btn btn-sm btn-outline-danger zs-btn zs-btn-neo" @click="removeAchat(a)">
                            <i class="fa-solid fa-trash"></i>
                          </button>
                        </div>
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
import { AchatsAPI } from "@/services/achats";
import { ArticlesAPI } from "@/services/articles";
import { unwrapList } from "@/services/pagination";

type Article = {
  id: number;
  nom_produit: string;
  reference: string;
  prix_achat: string;
  prix_vente: string;
  quantite_stock: number;
};

type Achat = any;

const loading = ref(false);
const error = ref("");

const achats = ref<Achat[]>([]);
const articles = ref<Article[]>([]);
const search = ref("");

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase();
  if (!q) return achats.value;
  return achats.value.filter((x: any) => (x.fournisseur || "").toLowerCase().includes(q));
});

const form = ref<any>({
  id: null as number | null,
  fournisseur: "",
  date_achat: null as string | null,
  note: "",
  lignes: [] as any[],
});

const isEditing = computed(() => !!form.value.id);

function formatAr(value: number | string) {
  const n = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(n)) return "0 Ar";
  return `${Math.round(n).toLocaleString("fr-FR")} Ar`;
}

function resetForm() {
  form.value = { id: null, fournisseur: "", date_achat: null, note: "", lignes: [] };
  error.value = "";
}

function addLine() {
  form.value.lignes.push({
    article: null,
    quantite: 1,
    prix_achat_unitaire: 0,
    prix_vente_unitaire: 0,
    maj_prix_article: true,
  });
}

function removeLine(idx: number) {
  form.value.lignes.splice(idx, 1);
}

function startCreate() {
  resetForm();
  addLine();
}

function startEdit(a: any) {
  error.value = "";
  form.value = {
    id: a.id,
    fournisseur: a.fournisseur || "",
    date_achat: a.date_achat || null,
    note: a.note || "",
    lignes: (a.lignes || []).map((l: any) => ({
      article: l.article,
      quantite: l.quantite,
      prix_achat_unitaire: l.prix_achat_unitaire,
      prix_vente_unitaire: l.prix_vente_unitaire,
      maj_prix_article: l.maj_prix_article ?? true,
    })),
  };
  if (form.value.lignes.length === 0) addLine();
}

async function loadAll() {
  loading.value = true;
  error.value = "";
  try {
    const [r1, r2] = await Promise.all([
      AchatsAPI.list(),
      ArticlesAPI.list(),
    ]);

    achats.value = unwrapList<any>(r1.data);
    articles.value = unwrapList<any>(r2.data);
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || "Impossible de charger les données.";
  } finally {
    loading.value = false;
  }
}

async function submit() {
  error.value = "";

  if (!form.value.lignes.length) {
    error.value = "Ajoute au moins une ligne.";
    return;
  }
  for (const l of form.value.lignes) {
    if (!l.article) {
      error.value = "Chaque ligne doit avoir un article.";
      return;
    }
    if (!l.quantite || l.quantite < 1) {
      error.value = "Quantité invalide.";
      return;
    }
  }

  loading.value = true;
  try {
    const payload = {
      fournisseur: form.value.fournisseur,
      date_achat: form.value.date_achat,
      note: form.value.note,
      lignes: form.value.lignes,
    };

    if (!form.value.id) await AchatsAPI.create(payload);
    else await AchatsAPI.update(form.value.id, payload);

    resetForm();
    await loadAll();
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

async function removeAchat(a: any) {
  const ok = confirm(`Supprimer l'achat #${a.id} ? (Cela va enlever le stock ajouté)`);
  if (!ok) return;

  loading.value = true;
  error.value = "";
  try {
    await AchatsAPI.remove(a.id);
    await loadAll();
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || "Impossible de supprimer.";
  } finally {
    loading.value = false;
  }
}

onMounted(loadAll);
</script>

<style scoped>
.min-width-0{ min-width:0; }

/* Search compact */
.zs-search{
  display:flex; align-items:center; gap:.5rem;
  padding: .35rem .6rem;
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,.08);
  background: rgba(255,255,255,.8);
}
.zs-search i{ opacity:.7; }
.zs-search-input{
  border: none !important;
  background: transparent !important;
  padding: 0 !important;
  min-width: 220px;
}
.zs-search-input:focus{ box-shadow:none !important; }

/* Inputs */
.zs-input{ border-radius: 12px; }

/* Empty */
.zs-empty{
  border: 1px dashed rgba(0,0,0,.15);
  border-radius: 14px;
  padding: 12px;
  color: rgba(108,117,125,1);
  background: rgba(248,249,250,1);
}

/* Line card */
.zs-line-card{
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 16px;
  padding: 12px;
  background: rgba(255,255,255,.9);
  box-shadow: 0 10px 24px rgba(0,0,0,.05);
  margin-bottom: 10px;
}

/* Table premium */
.zs-table-wrap{ border-radius: 16px; overflow:hidden; }
.zs-table thead th{
  background: rgba(248,249,250,1);
  font-weight: 700;
  color: rgba(33,37,41,.75);
  border-bottom: 1px solid rgba(0,0,0,.06);
}
.zs-table tbody tr:hover{ background: rgba(13,110,253,.04); }
.zs-table td, .zs-table th{ padding: .85rem .9rem; }

/* ellipsis */
.zs-ellipsis2{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
</style>
