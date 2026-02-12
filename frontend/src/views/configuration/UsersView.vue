<script setup lang="ts">
import { useUsersView } from "./assets/js/useUsersView";

const {
  isAdmin, q, role, actif, loading, items, errorMsg, roles,
  selected, editRole, editActive,
  badgeClass, roleLabel, load, openEdit, saveEdit,
} = useUsersView();
</script>

<template>
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
</template>

<style scoped src="@/views/configuration/assets/css/UsersView.css"></style>
