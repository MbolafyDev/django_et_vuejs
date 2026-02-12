<template>
  <div class="zs-root">
    <div class="container-fluid py-4 zs-admin">
      <!-- HERO -->
      <div class="zs-hero mb-3">
        <div class="d-flex align-items-start justify-content-between flex-wrap gap-3">
          <div class="min-width-0">
            <div class="d-flex align-items-center gap-2 flex-wrap">
              <div class="zs-dot"></div>
              <h4 class="mb-0 zs-title">Clients</h4>
              <span class="zs-pill-soft">
                <i class="fa-solid fa-id-card me-1"></i> CRM & Contacts
              </span>
            </div>

            <div class="text-muted small mt-1">
              Créer • modifier • supprimer • recherche instantanée
            </div>

            <!-- KPIs -->
            <div class="zs-kpis mt-3">
              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-users"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Total</div>
                  <div class="zs-kpi-value">{{ clients.length }}</div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-magnifying-glass"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Résultats</div>
                  <div class="zs-kpi-value">{{ filteredClients.length }}</div>
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

          <!-- ACTIONS -->
          <div class="d-flex align-items-center gap-2 flex-wrap">
            <div class="zs-search">
              <i class="fa-solid fa-magnifying-glass"></i>
              <input
                v-model="search"
                type="text"
                class="form-control form-control-sm zs-input zs-search-input"
                placeholder="Rechercher (nom, adresse, contact)"
              />
            </div>

            <button class="btn btn-primary zs-btn zs-btn-neo" @click="startCreate" title="Nouveau">
              <i class="fa-solid fa-plus"></i>
              <span class="ms-2 d-none d-sm-inline">Nouveau</span>
            </button>

            <button class="btn btn-outline-secondary zs-btn zs-btn-neo" :disabled="loading" @click="loadClients" title="Rafraîchir">
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
        <!-- FORM -->
        <div class="col-12 col-lg-4">
          <div class="zs-panel">
            <div class="zs-panel-head d-flex align-items-center justify-content-between flex-wrap gap-2">
              <div class="d-flex align-items-center gap-2 min-width-0">
                <i class="fa-solid fa-user-pen me-1 text-primary"></i>
                <span class="fw-bold">{{ isEditing ? "Modifier client" : "Nouveau client" }}</span>
              </div>

              <button v-if="isEditing" class="btn btn-sm btn-outline-secondary zs-btn zs-btn-neo" @click="resetForm">
                Annuler
              </button>
            </div>

            <div class="zs-panel-body">
              <div class="mb-2">
                <label class="form-label small text-muted mb-1">Nom *</label>
                <input
                  v-model="form.nom"
                  type="text"
                  class="form-control form-control-sm zs-input"
                  placeholder="Ex: RAKOTO Jean"
                  :disabled="loading"
                />
              </div>

              <div class="mb-2">
                <label class="form-label small text-muted mb-1">Adresse</label>
                <input
                  v-model="form.adresse"
                  type="text"
                  class="form-control form-control-sm zs-input"
                  placeholder="Ex: Antananarivo"
                  :disabled="loading"
                />
              </div>

              <div class="mb-3">
                <label class="form-label small text-muted mb-1">Contact</label>
                <input
                  v-model="form.contact"
                  type="text"
                  class="form-control form-control-sm zs-input"
                  placeholder="Téléphone / email"
                  :disabled="loading"
                />
              </div>

              <div class="d-grid">
                <button class="btn btn-primary zs-btn zs-btn-neo" :disabled="loading" @click="submit">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else :class="isEditing ? 'fa-solid fa-floppy-disk' : 'fa-solid fa-plus'" class="me-2"></i>
                  {{ isEditing ? "Enregistrer" : "Créer" }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- LIST -->
        <div class="col-12 col-lg-8">
          <div class="zs-panel">
            <div class="zs-panel-head d-flex align-items-center justify-content-between flex-wrap gap-2">
              <div class="d-flex align-items-center gap-2 min-width-0">
                <i class="fa-solid fa-list me-1 text-primary"></i>
                <span class="fw-bold">Liste des clients</span>
                <span class="zs-pill-count">{{ filteredClients.length }}</span>
              </div>

              <div class="text-muted small">Nom • Adresse • Contact</div>
            </div>

            <div class="zs-panel-body p-0">
              <div v-if="loading" class="p-3 text-muted">
                <span class="spinner-border spinner-border-sm me-2"></span>Chargement...
              </div>

              <div v-else-if="filteredClients.length === 0" class="p-4 text-center text-muted">
                <i class="fa-solid fa-circle-info me-1"></i> Aucun client.
              </div>

              <div v-else class="table-responsive zs-table-wrap">
                <table class="table table-sm align-middle mb-0 zs-table">
                  <thead>
                    <tr>
                      <th>Nom</th>
                      <th>Adresse</th>
                      <th>Contact</th>
                      <th class="text-end" style="width: 190px;">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="c in filteredClients" :key="c.id">
                      <td class="fw-semibold zs-ellipsis2">{{ c.nom }}</td>
                      <td class="text-muted zs-ellipsis2">{{ c.adresse || "—" }}</td>
                      <td class="text-muted zs-ellipsis2">{{ c.contact || "—" }}</td>
                      <td class="text-end">
                        <div class="d-inline-flex gap-2">
                          <button class="btn btn-sm btn-outline-primary zs-btn zs-btn-neo" @click="startEdit(c)" title="Modifier">
                            <i class="fa-solid fa-pen"></i>
                          </button>
                          <button class="btn btn-sm btn-outline-danger zs-btn zs-btn-neo" @click="removeClient(c)" title="Supprimer">
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
import { useClientsView } from "@/views/clients/assets/js/useClientsView";

const {
  loading, error,
  clients, search, filteredClients,
  form, isEditing,
  resetForm,
  loadClients,
  startCreate,
  startEdit,
  submit,
  removeClient,
} = useClientsView();
</script>

<style scoped src="@/views/clients/assets/css/ClientsView.css"></style>
