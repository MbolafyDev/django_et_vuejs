<template>
  <div class="zs-admin">
    <div class="container-fluid py-4">
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
import { useLieuxLivraison } from "@/views/livraison/assets/js/useLieuxLivraison";

const {
  loading, error,
  lieux, search,

  filteredLieux,
  actifsCount, inactifsCount,

  form, isEditing,

  labelCat, formatAr,

  resetForm, startCreate, startEdit,
  loadLieux, submit, removeLieu,
} = useLieuxLivraison();
</script>

<style scoped src="@/views/livraison/assets/css/LieuxLivraisonView.css"></style>
