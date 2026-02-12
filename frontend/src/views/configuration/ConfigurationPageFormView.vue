<template>
  <div class="container py-4" style="max-width: 800px;">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h4 class="mb-0">{{ mode === "create" ? "Ajouter une page" : "Modifier la page" }}</h4>
        <div class="text-muted small">Nom, lien, logo</div>
      </div>
      <button class="btn btn-outline-secondary" @click="back">Retour</button>
    </div>

    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-muted">Chargement...</div>

        <div v-else>
          <div class="row g-2">
            <div class="col-md-6">
              <label class="form-label">Nom</label>
              <input v-model="nom" class="form-control" />
            </div>

            <div class="col-md-6">
              <label class="form-label">Lien</label>
              <input v-model="lien" class="form-control" placeholder="/encaissement ou https://..." />
            </div>

            <div class="col-md-6">
              <label class="form-label">Logo</label>
              <input type="file" class="form-control" @change="onFile" />
            </div>

            <div class="col-12" v-if="logoPreview">
              <div class="text-muted small mb-1">Aperçu</div>
              <img :src="logoPreview" style="max-width: 120px; border-radius: 10px;" />
            </div>

            <div class="col-12">
              <div class="alert alert-info py-2 mb-0">
                Toutes les pages enregistrées sont <strong>actives</strong> automatiquement.
              </div>
            </div>
          </div>

          <div class="d-flex justify-content-end mt-3">
            <button class="btn btn-primary" :disabled="saving" @click="save">
              Enregistrer
            </button>
          </div>

          <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ mode: "create" | "edit"; id?: number }>();
import { useConfigurationPageForm } from "./assets/js/useConfigurationPageForm";

const { loading, saving, error, nom, lien, logoPreview, back, onFile, save } =
  useConfigurationPageForm(props);
</script>
