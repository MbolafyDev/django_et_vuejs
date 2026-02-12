<template>
  <div class="zs-admin">
    <div class="container-fluid py-4">
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
                        <span class="zs-pill-soft" :class="x.frais_override === null ? 'zs-pill-muted' : 'zs-pill-warn'">
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
import { useFraisLivraison } from "@/views/livraison/assets/js/useFraisLivraison";

const {
  loading, error,

  lieux, fraisList,
  search, filteredFrais,

  form, overrideEnabled, preview, isEditing,

  labelCat, formatAr,

  resetForm, startCreate, startEdit,
  loadFrais, submit, removeFrais,
} = useFraisLivraison();
</script>

<style scoped src="@/views/livraison/assets/css/FraisLivraisonView.css"></style>
