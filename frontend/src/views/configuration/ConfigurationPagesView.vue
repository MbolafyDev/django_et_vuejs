<template>
  <div>
    <AppNavbar />

    <div class="container py-4">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h4 class="mb-0">Pages</h4>
          <div class="text-muted small">Nom, lien, logo, ordre, actif</div>
        </div>
        <div class="d-flex gap-2">
          <router-link class="btn btn-primary" :to="{name:'configuration_pages_new'}">
            Ajouter une page
          </router-link>
          <button class="btn btn-outline-secondary" @click="load" :disabled="loading">
            <i class="fa-solid fa-rotate"></i>
          </button>
        </div>
      </div>

      <div class="table-responsive">
        <table class="table table-sm table-hover align-middle">
          <thead>
            <tr>
              <th>Logo</th>
              <th>Nom</th>
              <th>Lien</th>
              <th>Ordre</th>
              <th>Actif</th>
              <th class="text-end">Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr v-if="!loading && rows.length === 0">
              <td colspan="6" class="text-center text-muted py-4">Aucune page</td>
            </tr>

            <tr v-for="p in rows" :key="p.id">
              <td style="width:60px">
                <img v-if="p.logo_url" :src="p.logo_url" style="width:40px;height:40px;object-fit:cover;border-radius:8px;" />
                <div v-else class="text-muted small">—</div>
              </td>
              <td class="fw-semibold">{{ p.nom }}</td>
              <td class="text-muted">{{ p.lien }}</td>
              <td>{{ p.ordre }}</td>
              <td>
                <span v-if="p.actif" class="badge text-bg-success">Actif</span>
                <span v-else class="badge text-bg-secondary">Inactif</span>
              </td>
              <td class="text-end">
                <router-link class="btn btn-sm btn-outline-primary" :to="{name:'configuration_pages_edit', params:{id:p.id}}">
                  Modifier
                </router-link>
                <button class="btn btn-sm btn-outline-danger ms-2" @click="remove(p.id)" :disabled="loading">
                  Supprimer
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppNavbar from "@/components/AppNavbar.vue";
import { ref, onMounted } from "vue";
import { ConfigurationAPI, type PageConfig } from "@/services/configuration";

const loading = ref(false);
const error = ref("");
const rows = ref<PageConfig[]>([]);

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const res = await ConfigurationAPI.listPages({ page_size: 200 });
    rows.value = res.data.results || [];
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Erreur chargement pages";
  } finally {
    loading.value = false;
  }
}

async function remove(id: number) {
  if (!confirm("Supprimer cette page ?")) return;
  loading.value = true;
  try {
    await ConfigurationAPI.deletePage(id);
    await load();
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>
