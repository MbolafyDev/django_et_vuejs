<template>
  <div>
    <AppNavbar />

    <div class="container py-4" style="max-width: 800px;">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h4 class="mb-0">{{ mode === 'create' ? 'Ajouter une page' : 'Modifier la page' }}</h4>
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
                <img :src="logoPreview" style="max-width:120px;border-radius:10px;" />
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
  </div>
</template>

<script setup lang="ts">
import AppNavbar from "@/components/AppNavbar.vue";
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ConfigurationAPI } from "@/services/configuration";

const props = defineProps<{ mode: "create" | "edit"; id?: number }>();

const router = useRouter();

const loading = ref(false);
const saving = ref(false);
const error = ref("");

const nom = ref("");
const lien = ref("");

const logoFile = ref<File | null>(null);
const logoPreview = ref<string | null>(null);

function back() {
  router.push({ name: "configuration_pages" });
}

function onFile(e: Event) {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0] || null;
  logoFile.value = file;
  logoPreview.value = file ? URL.createObjectURL(file) : null;
}

async function load() {
  if (props.mode !== "edit" || !props.id) return;

  loading.value = true;
  error.value = "";
  try {
    const res = await ConfigurationAPI.getPage(props.id);
    const p = res.data as any;

    nom.value = p.nom || "";
    lien.value = p.lien || "";
    logoPreview.value = p.logo_url || null;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Erreur chargement page";
  } finally {
    loading.value = false;
  }
}

async function save() {
  error.value = "";

  if (!nom.value.trim()) { error.value = "Nom obligatoire"; return; }
  if (!lien.value.trim()) { error.value = "Lien obligatoire"; return; }

  saving.value = true;
  try {
    const fd = new FormData();
    fd.append("nom", nom.value.trim());
    fd.append("lien", lien.value.trim());
    if (logoFile.value) fd.append("logo", logoFile.value);

    // ✅ on n'envoie plus ordre/actif/config
    if (props.mode === "create") {
      await ConfigurationAPI.createPage(fd);
    } else {
      await ConfigurationAPI.updatePage(props.id!, fd);
    }
    back();
  } catch (e: any) {
    error.value =
      e?.response?.data?.detail ||
      JSON.stringify(e?.response?.data || e) ||
      "Erreur sauvegarde";
  } finally {
    saving.value = false;
  }
}

onMounted(load);
</script>
