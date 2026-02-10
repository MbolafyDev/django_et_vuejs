<template>
  <div>
    <AppNavbar />

    <div class="container py-4" style="max-width: 900px;">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h4 class="mb-0">Configuration</h4>
          <div class="text-muted small">Contrôle global de l’application</div>
        </div>
        <router-link class="btn btn-outline-primary" :to="{name:'configuration_pages'}">
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
                <input v-model="maintenance_message" class="form-control" placeholder="Ex: Site en maintenance, revenez plus tard..." />
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

  </div>
</template>

<script setup lang="ts">
import AppNavbar from "@/components/AppNavbar.vue";
import { ref, onMounted } from "vue";
import { ConfigurationAPI } from "@/services/configuration";

const loading = ref(false);
const saving = ref(false);

const app_name = ref("");
const maintenance_mode = ref(false);
const maintenance_message = ref("");

const error = ref("");
const success = ref("");

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const res = await ConfigurationAPI.getSolo();
    const data = res.data;

    app_name.value = data.app_name || "";
    maintenance_mode.value = !!data.maintenance_mode;
    maintenance_message.value = data.maintenance_message || "";
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Erreur chargement configuration";
  } finally {
    loading.value = false;
  }
}

async function save() {
  saving.value = true;
  error.value = "";
  success.value = "";
  try {
    await ConfigurationAPI.patchSolo({
      app_name: app_name.value,
      maintenance_mode: maintenance_mode.value,
      maintenance_message: maintenance_message.value,
    });
    success.value = "Configuration enregistrée.";
  } catch (e: any) {
    error.value = e?.response?.data?.detail || JSON.stringify(e?.response?.data || e) || "Erreur sauvegarde";
  } finally {
    saving.value = false;
  }
}

onMounted(load);
</script>
