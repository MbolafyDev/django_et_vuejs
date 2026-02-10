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

            <button
              class="btn btn-outline-secondary zs-btn zs-btn-neo"
              :disabled="loading"
              @click="loadClients"
              title="Rafraîchir"
            >
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

              <button
                v-if="isEditing"
                class="btn btn-sm btn-outline-secondary zs-btn zs-btn-neo"
                @click="resetForm"
              >
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

              <div class="text-muted small">
                Nom • Adresse • Contact
              </div>
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
import { onMounted, ref, computed } from "vue";
import AppNavbar from "@/components/AppNavbar.vue";
import { ClientsAPI } from "@/services/clients";

type Client = {
  id: number;
  nom: string;
  adresse: string;
  contact: string;
};

const loading = ref(false);
const error = ref("");

const clients = ref<Client[]>([]);
const search = ref("");

const filteredClients = computed(() => {
  const q = search.value.trim().toLowerCase();
  if (!q) return clients.value;
  return clients.value.filter((c) => {
    return (
      (c.nom || "").toLowerCase().includes(q) ||
      (c.adresse || "").toLowerCase().includes(q) ||
      (c.contact || "").toLowerCase().includes(q)
    );
  });
});

const form = ref<{ id?: number; nom: string; adresse: string; contact: string }>({
  nom: "",
  adresse: "",
  contact: "",
});

const isEditing = computed(() => !!form.value.id);

function resetForm() {
  form.value = { nom: "", adresse: "", contact: "" };
  error.value = "";
}

async function loadClients() {
  loading.value = true;
  error.value = "";
  try {
    const res = await ClientsAPI.list();
    clients.value = res.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || "Impossible de charger les clients.";
  } finally {
    loading.value = false;
  }
}

function startCreate() {
  resetForm();
}

function startEdit(c: Client) {
  error.value = "";
  form.value = {
    id: c.id,
    nom: c.nom || "",
    adresse: c.adresse || "",
    contact: c.contact || "",
  };
}

async function submit() {
  error.value = "";

  if (!form.value.nom.trim()) {
    error.value = "Le champ 'nom' est obligatoire.";
    return;
  }

  loading.value = true;

  try {
    if (!form.value.id) {
      const res = await ClientsAPI.create({
        nom: form.value.nom.trim(),
        adresse: form.value.adresse.trim(),
        contact: form.value.contact.trim(),
      });
      clients.value = [res.data, ...clients.value];
      resetForm();
    } else {
      const id = form.value.id;
      const res = await ClientsAPI.update(id, {
        nom: form.value.nom.trim(),
        adresse: form.value.adresse.trim(),
        contact: form.value.contact.trim(),
      });
      clients.value = clients.value.map((c) => (c.id === id ? res.data : c));
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

async function removeClient(c: Client) {
  const ok = confirm(`Supprimer le client "${c.nom}" ?`);
  if (!ok) return;

  loading.value = true;
  error.value = "";

  try {
    await ClientsAPI.remove(c.id);
    clients.value = clients.value.filter((x) => x.id !== c.id);
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || "Impossible de supprimer le client.";
  } finally {
    loading.value = false;
  }
}

onMounted(loadClients);
</script>

<style scoped>
.min-width-0{ min-width:0; }

/* Search compact (même style que tes pages zs) */
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
  min-width: 280px;
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

.zs-ellipsis2{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
</style>
