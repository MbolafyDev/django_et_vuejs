<template>
  <div class="zs-root">
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
                  <img :src="photoPreview || form.photo_url" alt="Aperçu" class="zs-photo-preview" />
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

              <div class="text-muted small">Nom / Référence / Photo</div>
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
                        <img v-if="a.photo_url" :src="a.photo_url" alt="photo" class="zs-photo-thumb" />
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
import { useArticlesView } from "@/views/article/assets/js/useArticlesView";

const {
  loading, error,
  articles, search, filteredArticles,
  form, photoPreview, isEditing,
  formatAr,
  onPhotoChange,
  resetForm,
  loadArticles,
  startCreate,
  startEdit,
  submit,
  removeArticle,
} = useArticlesView();
</script>

<style scoped src="@/views/article/assets/css/ArticlesView.css"></style>
