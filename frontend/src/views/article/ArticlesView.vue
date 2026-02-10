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
              <h4 class="mb-0 zs-title">Articles</h4>
              <span class="zs-pill-soft">
                <i class="fa-solid fa-box me-1"></i> Produits & Photos
              </span>
            </div>

            <div class="text-muted small mt-1">
              Gestion des produits • prix • description • image
            </div>

            <!-- KPIs -->
            <div class="zs-kpis mt-3">
              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-boxes-stacked"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Articles</div>
                  <div class="zs-kpi-value">{{ articles.length }}</div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-filter"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Filtre</div>
                  <div class="zs-kpi-value">
                    <span v-if="search.trim()" class="text-primary fw-bold">ON</span>
                    <span v-else class="text-muted">OFF</span>
                  </div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-image"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Photos</div>
                  <div class="zs-kpi-value">
                    {{ articles.filter(a => !!a.photo_url).length }}
                  </div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-pen-to-square"></i></div>
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
                placeholder="Rechercher (nom / ref)"
              />
            </div>

            <button class="btn btn-primary zs-btn zs-btn-neo" @click="startCreate" title="Nouveau">
              <i class="fa-solid fa-plus"></i>
              <span class="ms-2 d-none d-sm-inline">Nouveau</span>
            </button>

            <button class="btn btn-outline-secondary zs-btn zs-btn-neo" :disabled="loading" @click="loadArticles" title="Rafraîchir">
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
            <div class="zs-panel-head d-flex align-items-center justify-content-between flex-wrap gap-2">
              <div class="d-flex align-items-center gap-2 min-width-0">
                <i class="fa-solid fa-box me-1 text-primary"></i>
                <span class="fw-bold">{{ isEditing ? "Modifier article" : "Nouveau article" }}</span>
              </div>

              <button v-if="isEditing" class="btn btn-sm btn-outline-secondary zs-btn zs-btn-neo" @click="resetForm">
                Annuler
              </button>
            </div>

            <div class="zs-panel-body">
              <div class="mb-2">
                <label class="form-label small text-muted mb-1">Nom produit *</label>
                <input v-model="form.nom_produit" class="form-control form-control-sm zs-input" :disabled="loading" />
              </div>

              <div class="mb-2">
                <label class="form-label small text-muted mb-1">Référence *</label>
                <input v-model="form.reference" class="form-control form-control-sm zs-input" :disabled="loading" />
              </div>

              <div class="row g-2">
                <div class="col-6">
                  <label class="form-label small text-muted mb-1">Prix d’achat (Ar)</label>
                  <input v-model="form.prix_achat" type="number" step="1" class="form-control form-control-sm zs-input" :disabled="loading" />
                </div>
                <div class="col-6">
                  <label class="form-label small text-muted mb-1">Prix de vente (Ar)</label>
                  <input v-model="form.prix_vente" type="number" step="1" class="form-control form-control-sm zs-input" :disabled="loading" />
                </div>
              </div>

              <div class="mb-2 mt-2">
                <label class="form-label small text-muted mb-1">Description</label>
                <textarea v-model="form.description" class="form-control form-control-sm zs-input" rows="3" :disabled="loading"></textarea>
              </div>

              <!-- Photo -->
              <div class="mb-3">
                <label class="form-label small text-muted mb-1">Photo</label>
                <input
                  type="file"
                  class="form-control form-control-sm zs-input"
                  accept="image/*"
                  @change="onPhotoChange"
                  :disabled="loading"
                />

                <div class="mt-2 d-flex gap-2 align-items-center" v-if="photoPreview || form.photo_url">
                  <img
                    :src="photoPreview || form.photo_url"
                    alt="Aperçu"
                    class="zs-photo-preview"
                  />
                  <div class="small text-muted">
                    Aperçu de la photo
                    <div class="zs-mini-note">Astuce : photo carrée = plus propre.</div>
                  </div>
                </div>
              </div>

              <div class="d-grid">
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
                <span class="zs-pill-count">{{ filteredArticles.length }}</span>
              </div>

              <div class="text-muted small">
                Nom / Référence / Photo
              </div>
            </div>

            <div class="zs-panel-body p-0">
              <div v-if="loading" class="p-3 text-muted">
                <span class="spinner-border spinner-border-sm me-2"></span>Chargement...
              </div>

              <div v-else-if="filteredArticles.length === 0" class="p-4 text-center text-muted">
                <i class="fa-solid fa-circle-info me-1"></i> Aucun article.
              </div>

              <div v-else class="table-responsive zs-table-wrap">
                <table class="table table-sm align-middle mb-0 zs-table">
                  <thead>
                    <tr>
                      <th style="width:70px;">Photo</th>
                      <th>Nom</th>
                      <th style="width:180px;">Référence</th>
                      <th class="text-end" style="width:160px;">Prix vente</th>
                      <th class="text-end" style="width:190px;">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="a in filteredArticles" :key="a.id">
                      <td>
                        <img
                          v-if="a.photo_url"
                          :src="a.photo_url"
                          alt="photo"
                          class="zs-photo-thumb"
                        />
                        <span v-else class="text-muted small">—</span>
                      </td>

                      <td class="fw-semibold zs-ellipsis2">{{ a.nom_produit }}</td>

                      <td class="text-muted">
                        <span class="zs-mono">{{ a.reference }}</span>
                      </td>

                      <td class="text-end fw-bold">{{ formatAr(a.prix_vente) }}</td>

                      <td class="text-end">
                        <div class="d-inline-flex gap-2">
                          <button class="btn btn-sm btn-outline-primary zs-btn zs-btn-neo" @click="startEdit(a)" title="Modifier">
                            <i class="fa-solid fa-pen"></i>
                          </button>
                          <button class="btn btn-sm btn-outline-danger zs-btn zs-btn-neo" @click="removeArticle(a)" title="Supprimer">
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
import { ArticlesAPI } from "@/services/articles";

type Article = {
  id: number;
  nom_produit: string;
  reference: string;
  prix_achat: string | number;
  prix_vente: string | number;
  description?: string | null;
  photo_url?: string | null;
};

const loading = ref(false);
const error = ref("");
const articles = ref<Article[]>([]);
const search = ref("");

const filteredArticles = computed(() => {
  const q = search.value.trim().toLowerCase();
  if (!q) return articles.value;
  return articles.value.filter((a) =>
    (a.nom_produit || "").toLowerCase().includes(q) ||
    (a.reference || "").toLowerCase().includes(q)
  );
});

const form = ref<{
  id?: number;
  nom_produit: string;
  reference: string;
  prix_achat: string;
  prix_vente: string;
  description: string;
  photo_url?: string | null;
}>( {
  nom_produit: "",
  reference: "",
  prix_achat: "0",
  prix_vente: "0",
  description: "",
  photo_url: null,
});

const photoFile = ref<File | null>(null);
const photoPreview = ref<string | null>(null);

const isEditing = computed(() => !!form.value.id);

function formatAr(value: string | number) {
  const n = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(n)) return "0 Ar";
  return `${Math.round(n).toLocaleString("fr-FR")} Ar`;
}

function onPhotoChange(e: Event) {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0] || null;
  photoFile.value = file;

  if (photoPreview.value) URL.revokeObjectURL(photoPreview.value);
  photoPreview.value = file ? URL.createObjectURL(file) : null;
}

function resetForm() {
  form.value = {
    nom_produit: "",
    reference: "",
    prix_achat: "0",
    prix_vente: "0",
    description: "",
    photo_url: null,
  };
  error.value = "";

  photoFile.value = null;
  if (photoPreview.value) URL.revokeObjectURL(photoPreview.value);
  photoPreview.value = null;
}

async function loadArticles() {
  loading.value = true;
  error.value = "";
  try {
    const res = await ArticlesAPI.list();
    articles.value = res.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || "Impossible de charger les articles.";
  } finally {
    loading.value = false;
  }
}

function startCreate() {
  resetForm();
}

function startEdit(a: Article) {
  error.value = "";
  form.value = {
    id: a.id,
    nom_produit: a.nom_produit || "",
    reference: a.reference || "",
    prix_achat: String(a.prix_achat ?? "0"),
    prix_vente: String(a.prix_vente ?? "0"),
    description: (a.description as any) || "",
    photo_url: a.photo_url ?? null,
  };

  photoFile.value = null;
  if (photoPreview.value) URL.revokeObjectURL(photoPreview.value);
  photoPreview.value = null;
}

async function submit() {
  error.value = "";

  if (!form.value.nom_produit.trim()) {
    error.value = "Le champ 'nom_produit' est obligatoire.";
    return;
  }
  if (!form.value.reference.trim()) {
    error.value = "Le champ 'reference' est obligatoire.";
    return;
  }

  loading.value = true;

  const fd = new FormData();
  fd.append("nom_produit", form.value.nom_produit.trim());
  fd.append("reference", form.value.reference.trim());
  fd.append("prix_achat", String(form.value.prix_achat ?? "0"));
  fd.append("prix_vente", String(form.value.prix_vente ?? "0"));
  fd.append("description", form.value.description.trim());

  if (photoFile.value) {
    fd.append("photo", photoFile.value);
  }

  try {
    if (!form.value.id) {
      const res = await ArticlesAPI.create(fd);
      articles.value = [res.data, ...articles.value];
      resetForm();
    } else {
      const id = form.value.id;
      const res = await ArticlesAPI.update(id, fd);
      articles.value = articles.value.map((x) => (x.id === id ? res.data : x));
      resetForm();
    }
  } catch (e: any) {
    const data = e?.response?.data;
    if (data && typeof data === "object") {
      const firstKey = Object.keys(data)[0];
      error.value = firstKey ? `${firstKey}: ${data[firstKey]?.[0] ?? ""}` : "Erreur validation.";
    } else {
      error.value = e?.message || "Erreur lors de l'enregistrement.";
    }
  } finally {
    loading.value = false;
  }
}

async function removeArticle(a: Article) {
  const ok = confirm(`Supprimer l'article "${a.nom_produit}" ?`);
  if (!ok) return;

  loading.value = true;
  error.value = "";

  try {
    await ArticlesAPI.remove(a.id);
    articles.value = articles.value.filter((x) => x.id !== a.id);
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || "Impossible de supprimer l'article.";
  } finally {
    loading.value = false;
  }
}

onMounted(loadArticles);
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
  min-width: 240px;
}
.zs-search-input:focus{ box-shadow:none !important; }

/* Inputs */
.zs-input{ border-radius: 12px; }

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

/* Photos */
.zs-photo-thumb{
  width: 44px;
  height: 44px;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid rgba(0,0,0,.08);
  box-shadow: 0 10px 24px rgba(0,0,0,.06);
}
.zs-photo-preview{
  width: 76px;
  height: 76px;
  object-fit: cover;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,.10);
  box-shadow: 0 10px 24px rgba(0,0,0,.08);
}
.zs-mini-note{ opacity:.8; }

/* ellipsis & mono */
.zs-ellipsis2{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.zs-mono{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
</style>
