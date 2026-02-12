<template>
  <div class="container py-4" style="max-width: 900px;">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h4 class="mb-0">Configuration</h4>
        <div class="text-muted small">Contrôle global de l’application</div>
      </div>
      <router-link class="btn btn-outline-primary" :to="{ name: 'configuration_pages' }">
        Gérer les pages
      </router-link>
    </div>

    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-muted">Chargement...</div>

        <div v-else>
          <div class="row g-2">
            <div class="col-md-6">
              <label class="form-label">Nom de l’application</label>
              <input v-model="app_name" class="form-control" />
            </div>

            <div class="col-md-6">
              <label class="form-label">Mode maintenance</label>
              <div class="form-check mt-2">
                <input class="form-check-input" type="checkbox" v-model="maintenance_mode" id="mnt" />
                <label class="form-check-label" for="mnt">Activer la maintenance</label>
              </div>
            </div>

            <div class="col-12">
              <label class="form-label">Message maintenance</label>
              <input
                v-model="maintenance_message"
                class="form-control"
                placeholder="Ex: Site en maintenance, revenez plus tard..."
              />
            </div>
          </div>

          <div class="d-flex justify-content-end mt-3">
            <button class="btn btn-primary" :disabled="saving" @click="save">
              Enregistrer
            </button>
          </div>

          <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
          <div v-if="success" class="alert alert-success mt-3">{{ success }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useConfigurationDashboard } from "./assets/js/useConfigurationDashboard";

const {
  loading,
  saving,
  app_name,
  maintenance_mode,
  maintenance_message,
  error,
  success,
  save,
} = useConfigurationDashboard();
</script>
