<!-- frontend/src/views/configuration/UsersView.vue -->
<script setup lang="ts">
import AppNavbar from "@/components/AppNavbar.vue";
import { computed, onMounted, ref } from "vue";
import Modal from "bootstrap/js/dist/modal";
import { ConfigUsersAPI, type UserItem, type UserRole } from "@/services/configuration_users";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const isAdmin = computed(() => auth.user?.role === "ADMIN" || (auth.user as any)?.is_staff || (auth.user as any)?.is_superuser);

const q = ref("");
const role = ref<string>("");
const actif = ref<string>(""); // "", "true", "false"

const loading = ref(false);
const items = ref<UserItem[]>([]);
const errorMsg = ref<string>("");

const roles: Array<{ value: UserRole; label: string }> = [
  { value: "ADMIN", label: "Admin" },
  { value: "UTILISATEUR", label: "Utilisateur" },
  { value: "COMMERCIALE", label: "Commerciale" },
  { value: "COMMUNITY_MANAGER", label: "Community manager" },
];

const selected = ref<UserItem | null>(null);
const editRole = ref<UserRole>("COMMERCIALE");
const editActive = ref(true);

function badgeClass(u: UserItem) {
  if (!u.is_active) return "badge text-bg-danger";
  if (u.role === "ADMIN") return "badge text-bg-primary";
  if (u.role === "UTILISATEUR") return "badge text-bg-success";
  return "badge text-bg-secondary";
}

function roleLabel(r: string) {
  return roles.find((x) => x.value === (r as any))?.label || r;
}

async function load() {
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await ConfigUsersAPI.list({
      q: q.value || undefined,
      role: (role.value as any) || undefined,
      actif: (actif.value as any) || undefined,
      page_size: 200,
    });

    const data: any = res.data;
    items.value = data?.results || data || [];
  } catch (e: any) {
    items.value = [];
    errorMsg.value = e?.response?.data?.detail || "Erreur lors du chargement des utilisateurs.";
  } finally {
    loading.value = false;
  }
}

function openEdit(u: UserItem) {
  selected.value = u;
  editRole.value = u.role;
  editActive.value = u.is_active;

  const el = document.getElementById("zsUserModal");
  if (!el) return;

  const modal = Modal.getOrCreateInstance(el);
  modal.show();
}

async function saveEdit() {
  if (!selected.value) return;

  const id = selected.value.id;
  loading.value = true;
  errorMsg.value = "";

  try {
    await ConfigUsersAPI.setStatus(id, editActive.value);

    if (editRole.value !== selected.value.role) {
      await ConfigUsersAPI.setRole(id, editRole.value);
    }

    await load();

    const el = document.getElementById("zsUserModal");
    if (el) Modal.getInstance(el)?.hide();
  } catch (e: any) {
    errorMsg.value =
      e?.response?.data?.detail ||
      (typeof e?.response?.data === "string" ? e.response.data : "") ||
      "Impossible de mettre à jour cet utilisateur.";
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div>
    <!-- ✅ NAVBAR (comme Dashboard) -->
    <AppNavbar />

    <!-- ✅ PAGE CONTENT -->
    <div class="container py-4" style="max-width: 1100px;">
      <div class="d-flex align-items-start justify-content-between gap-3 flex-wrap">
        <div>
          <h3 class="mb-1 fw-black">Gestion des utilisateurs</h3>
          <div class="text-muted small">
            Modifier le <b>rôle</b> et le <b>statut</b> des comptes.
            <span v-if="isAdmin" class="ms-2 badge text-bg-primary">ADMIN</span>
          </div>
        </div>

        <button class="btn btn-outline-primary zs-btn" @click="load" :disabled="loading">
          <i class="fa-solid fa-rotate me-2"></i> Rafraîchir
        </button>
      </div>

      <!-- Filters -->
      <div class="card shadow-sm border-0 mt-3">
        <div class="card-body">
          <div class="row g-2">
            <div class="col-12 col-lg-5">
              <label class="form-label small fw-bold text-muted">Recherche</label>
              <div class="input-group">
                <span class="input-group-text"><i class="fa-solid fa-magnifying-glass"></i></span>
                <input v-model="q" class="form-control" placeholder="username, email, nom..." @keyup.enter="load" />
                <button class="btn btn-primary" @click="load" :disabled="loading">
                  <i class="fa-solid fa-search"></i>
                </button>
              </div>
            </div>

            <div class="col-12 col-lg-4">
              <label class="form-label small fw-bold text-muted">Rôle</label>
              <select v-model="role" class="form-select" @change="load">
                <option value="">Tous</option>
                <option v-for="r in roles" :key="r.value" :value="r.value">{{ r.label }}</option>
              </select>
            </div>

            <div class="col-12 col-lg-3">
              <label class="form-label small fw-bold text-muted">Statut</label>
              <select v-model="actif" class="form-select" @change="load">
                <option value="">Tous</option>
                <option value="true">Actifs</option>
                <option value="false">Inactifs</option>
              </select>
            </div>
          </div>

          <div v-if="errorMsg" class="alert alert-danger mt-3 mb-0">
            <i class="fa-solid fa-triangle-exclamation me-2"></i> {{ errorMsg }}
          </div>
        </div>
      </div>

      <!-- Table -->
      <div class="card shadow-sm border-0 mt-3">
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th class="ps-3">Utilisateur</th>
                  <th>Email</th>
                  <th>Rôle</th>
                  <th>Statut</th>
                  <th class="text-end pe-3" style="width: 1%;">Actions</th>
                </tr>
              </thead>

              <tbody v-if="loading">
                <tr><td colspan="5" class="p-4 text-center text-muted">Chargement…</td></tr>
              </tbody>

              <tbody v-else-if="items.length === 0">
                <tr><td colspan="5" class="p-4 text-center text-muted">Aucun utilisateur.</td></tr>
              </tbody>

              <tbody v-else>
                <tr v-for="u in items" :key="u.id">
                  <td class="ps-3">
                    <div class="d-flex align-items-center gap-2">
                      <span v-if="u.photo_profil_url" class="zs-avatar">
                        <img :src="u.photo_profil_url" alt="" />
                      </span>
                      <span v-else class="zs-dot"></span>

                      <div class="min-w-0">
                        <div class="fw-bold zs-ellipsis">
                          {{ (u.first_name || '') }} {{ (u.last_name || '') }}
                          <span class="text-muted" v-if="!(u.first_name || u.last_name)">({{ u.username }})</span>
                        </div>
                        <div class="small text-muted zs-ellipsis">@{{ u.username }}</div>
                      </div>
                    </div>
                  </td>

                  <td class="text-muted">{{ u.email }}</td>

                  <td><span :class="badgeClass(u)">{{ roleLabel(u.role) }}</span></td>

                  <td>
                    <span v-if="u.is_active" class="badge text-bg-success">Actif</span>
                    <span v-else class="badge text-bg-danger">Inactif</span>
                  </td>

                  <td class="text-end pe-3">
                    <button class="btn btn-sm btn-outline-primary" @click="openEdit(u)">
                      <i class="fa-solid fa-pen-to-square me-1"></i>
                    </button>
                  </td>
                </tr>
              </tbody>

            </table>
          </div>
        </div>
      </div>

      <!-- Modal edit -->
      <div class="modal fade" id="zsUserModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow">
            <div class="modal-header">
              <h5 class="modal-title fw-black">
                <i class="fa-solid fa-user-gear me-2 text-primary"></i> Mettre à jour
              </h5>
              <button class="btn-close" type="button" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>

            <div class="modal-body" v-if="selected">
              <div class="mb-3">
                <div class="small text-muted fw-bold">Utilisateur</div>
                <div class="fw-bold">{{ selected.first_name }} {{ selected.last_name }}</div>
                <div class="text-muted small">{{ selected.email }}</div>
              </div>

              <div class="mb-3">
                <label class="form-label small fw-bold text-muted">Rôle</label>
                <select v-model="editRole" class="form-select">
                  <option v-for="r in roles" :key="r.value" :value="r.value">{{ r.label }}</option>
                </select>
                <div class="form-text">Promotion vers <b>ADMIN</b> autorisée uniquement si tu es ADMIN.</div>
              </div>

              <div class="mb-2">
                <label class="form-label small fw-bold text-muted">Statut</label>
                <div class="form-check form-switch">
                  <input class="form-check-input" type="checkbox" v-model="editActive" id="zsActiveSwitch" />
                  <label class="form-check-label" for="zsActiveSwitch">
                    {{ editActive ? "Actif" : "Inactif" }}
                  </label>
                </div>
              </div>

              <div v-if="errorMsg" class="alert alert-danger mt-3 mb-0">
                <i class="fa-solid fa-triangle-exclamation me-2"></i> {{ errorMsg }}
              </div>
            </div>

            <div class="modal-footer">
              <button class="btn btn-outline-secondary" type="button" data-bs-dismiss="modal">Annuler</button>
              <button class="btn btn-primary" type="button" @click="saveEdit" :disabled="loading">
                <i class="fa-solid fa-floppy-disk me-2"></i> Enregistrer
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.fw-black { font-weight: 950; }

.zs-dot{
  width: 10px; height: 10px; border-radius: 999px;
  background: rgba(25,135,84,1);
  box-shadow: 0 0 0 4px rgba(25,135,84,.14);
}
.zs-avatar{
  width: 34px; height: 34px; border-radius: 14px;
  overflow: hidden; border: 1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.8);
  flex: 0 0 auto;
}
.zs-avatar img{ width:100%; height:100%; object-fit:cover; }

.zs-ellipsis{ max-width: 280px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.min-w-0{ min-width:0; }
.zs-btn{ border-radius: 14px; }
</style>
