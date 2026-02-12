<template>
  <div class="zs-root">
    <div class="container-fluid py-4 zs-admin">
      <!-- HERO -->
      <div class="zs-hero mb-3">
        <div class="d-flex align-items-start justify-content-between flex-wrap gap-3">
          <div class="min-width-0">
            <div class="d-flex align-items-center gap-2 flex-wrap">
              <div class="zs-dot"></div>
              <h4 class="mb-0 zs-title">Livraisons</h4>
              <span class="zs-pill-soft">
                <i class="fa-solid fa-truck-fast me-1"></i> Programmation & Suivi
              </span>
            </div>

            <div class="text-muted small mt-1">
              Programmer les commandes • suivi • actions • historique
            </div>

            <!-- KPIs -->
            <div class="zs-kpis mt-3">
              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-list-check"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Commandes à programmer</div>
                  <div class="zs-kpi-value">{{ totalCmd }}</div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-truck"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Livraisons</div>
                  <div class="zs-kpi-value">{{ total }}</div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-filter"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Filtres</div>
                  <div class="zs-kpi-value">
                    <span v-if="hasActiveFilters" class="text-primary fw-bold">ON</span>
                    <span v-else class="text-muted">OFF</span>
                  </div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-wand-magic-sparkles"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Sync</div>
                  <div class="zs-kpi-value">
                    <span v-if="loading" class="text-warning fw-bold">...</span>
                    <span v-else class="text-success fw-bold">OK</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="d-flex gap-2 flex-wrap align-items-center">
            <button class="btn btn-outline-secondary zs-btn zs-btn-neo" @click="refreshAll()" :disabled="loading || loadingCmd" title="Rafraîchir">
              <i class="fa-solid fa-rotate"></i>
              <span class="ms-2 d-none d-sm-inline">Rafraîchir</span>
            </button>

            <button class="btn btn-outline-primary zs-btn zs-btn-neo" @click="sync" :disabled="loading" title="Sync">
              <i class="fa-solid fa-wand-magic-sparkles"></i>
              <span class="ms-2 d-none d-sm-inline">Sync</span>
            </button>

            <button class="btn btn-outline-primary zs-btn zs-btn-neo" @click="toggleFilters" title="Filtres">
              <i class="fa-solid fa-filter me-1"></i>
              Filtres
              <span v-if="hasActiveFilters" class="zs-dot-mini ms-2"></span>
            </button>

            <button
              v-if="hasActiveFilters"
              class="btn btn-outline-danger zs-btn zs-btn-neo"
              @click="resetFilters"
              :disabled="loading"
              title="Réinitialiser"
            >
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- ERROR -->
      <div v-if="error" class="alert alert-danger py-2">
        <i class="fa-solid fa-triangle-exclamation me-2"></i>{{ error }}
      </div>

      <!-- ✅ PANEL: Commandes à programmer -->
      <div class="zs-panel mb-3">
        <div class="zs-panel-head d-flex align-items-center justify-content-between flex-wrap gap-2">
          <div class="d-flex align-items-center gap-2 min-width-0">
            <i class="fa-solid fa-calendar-check me-1 text-primary"></i>
            <span class="fw-bold">Commandes à programmer</span>
            <span class="zs-pill-count">{{ totalCmd }}</span>
          </div>
          <div class="text-muted small">
            Toutes les commandes non finalisées (même sans livraison)
          </div>
        </div>

        <div class="zs-panel-body p-0">
          <div v-if="loadingCmd" class="p-3 text-muted">
            <span class="spinner-border spinner-border-sm me-2"></span>Chargement...
          </div>

          <div v-else>
            <div v-if="commandes.length === 0" class="p-4 text-center text-muted">
              <i class="fa-solid fa-circle-info me-1"></i> Aucune commande à programmer.
            </div>

            <div v-else class="table-responsive zs-table-wrap">
              <table class="table table-sm align-middle mb-0 zs-table">
                <thead>
                  <tr>
                    <th style="width: 110px;">#</th>
                    <th>Client</th>
                    <th>Adresse</th>
                    <th style="width: 200px;">Date livraison</th>
                    <th style="width: 160px;">Livraison</th>
                    <th style="width: 180px;" class="text-end">Action</th>
                  </tr>
                </thead>

                <tbody>
                  <tr v-for="c in commandes" :key="c.id">
                    <td class="fw-bold">Cmd #{{ c.id }}</td>

                    <td>
                      <div class="fw-semibold zs-ellipsis2">{{ c.client_nom }}</div>
                      <div class="text-muted small zs-ellipsis2">{{ c.client_contact }}</div>
                    </td>

                    <td>
                      <div class="zs-ellipsis2">{{ c.client_adresse }}</div>
                      <div class="text-muted small zs-ellipsis2">{{ c.precision_lieu }}</div>
                    </td>

                    <td>
                      <input type="date" class="form-control form-control-sm zs-input" v-model="programmationDates[c.id]" />
                      <div class="text-muted small mt-1">
                        Actuelle: <span class="fw-semibold">{{ c.date_livraison || "-" }}</span>
                      </div>
                    </td>

                    <td>
                      <span v-if="c.livraison_id" class="zs-status zs-st zs-st-done">
                        <span class="zs-status-dot"></span>
                        L{{ c.livraison_id }} — {{ c.livraison_statut }}
                      </span>
                      <span v-else class="zs-status zs-st zs-st-cancel">
                        <span class="zs-status-dot"></span>
                        Aucune
                      </span>
                    </td>

                    <td class="text-end">
                      <button class="btn btn-sm btn-primary zs-btn zs-btn-neo" @click="programmer(c)" :disabled="loading || !programmationDates[c.id]">
                        <i class="fa-solid fa-calendar-check me-1"></i>
                        Programmer
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="zs-panel-foot border-top">
              <div class="small text-muted">Total: {{ totalCmd }}</div>
              <div class="d-flex gap-2">
                <button class="btn btn-sm btn-outline-secondary zs-btn zs-btn-neo" @click="prevCmd" :disabled="!prevCmdUrl || loadingCmd">
                  <i class="fa-solid fa-chevron-left me-1"></i> Précédent
                </button>
                <button class="btn btn-sm btn-outline-secondary zs-btn zs-btn-neo" @click="nextCmd" :disabled="!nextCmdUrl || loadingCmd">
                  Suivant <i class="fa-solid fa-chevron-right ms-1"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- FILTERS -->
      <div v-if="showFilters" class="zs-panel mb-3">
        <div class="zs-panel-head">
          <div class="fw-bold">
            <i class="fa-solid fa-sliders me-2 text-primary"></i> Filtres livraisons
          </div>
        </div>

        <div class="zs-panel-body">
          <div class="row g-2 align-items-end">
            <div class="col-12 col-md-4">
              <label class="form-label small text-muted mb-1">Recherche</label>
              <input v-model="filters.q" class="form-control form-control-sm zs-input" placeholder="Client, téléphone, lieu, #commande..." />
            </div>

            <div class="col-6 col-md-3">
              <label class="form-label small text-muted mb-1">Statut</label>
              <select v-model="filters.statut" class="form-select form-select-sm zs-input">
                <option value="">Tous</option>
                <option value="A_PREPARER">À préparer</option>
                <option value="EN_LIVRAISON">En livraison</option>
                <option value="LIVREE">Livrée</option>
                <option value="REPORTEE">Reportée</option>
                <option value="ANNULEE">Annulée</option>
              </select>
            </div>

            <div class="col-6 col-md-3">
              <label class="form-label small text-muted mb-1">Date prévue</label>
              <input v-model="filters.date_prevue" type="date" class="form-control form-control-sm zs-input" />
            </div>

            <div class="col-12 col-md-2 d-grid">
              <button class="btn btn-primary zs-btn zs-btn-neo" @click="applyFilters" :disabled="loading">
                <i class="fa-solid fa-filter me-1"></i> Filtrer
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ✅ PANEL: List livraisons -->
      <div class="zs-panel">
        <div class="zs-panel-head d-flex align-items-center justify-content-between flex-wrap gap-2">
          <div class="d-flex align-items-center gap-2 min-width-0">
            <i class="fa-solid fa-truck me-1 text-primary"></i>
            <span class="fw-bold">Livraisons</span>
            <span class="zs-pill-count">{{ total }}</span>
          </div>
          <div class="text-muted small">Suivi & actions</div>
        </div>

        <div class="zs-panel-body p-0">
          <div v-if="loading" class="p-3 text-muted">
            <span class="spinner-border spinner-border-sm me-2"></span>Chargement...
          </div>

          <div v-else>
            <div v-if="items.length === 0" class="p-4 text-center text-muted">
              <i class="fa-solid fa-circle-info me-1"></i> Aucune livraison.
            </div>

            <div v-else class="table-responsive zs-table-wrap">
              <table class="table table-sm align-middle mb-0 zs-table">
                <thead>
                  <tr>
                    <th style="width: 110px;">#</th>
                    <th>Client</th>
                    <th>Lieu</th>
                    <th style="width: 160px;">Date</th>
                    <th style="width: 170px;">Statut</th>
                    <th style="width: 300px;" class="text-end">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="l in items" :key="l.id">
                    <td>
                      <div class="fw-bold">L{{ l.id }}</div>
                      <div class="text-muted small">Cmd #{{ l.commande_detail.id }}</div>
                    </td>

                    <td>
                      <div class="fw-semibold zs-ellipsis2">{{ l.commande_detail.client_nom }}</div>
                      <div class="text-muted small zs-ellipsis2">{{ l.commande_detail.client_contact }}</div>
                    </td>

                    <td>
                      <div class="zs-ellipsis2">{{ l.commande_detail.client_adresse }}</div>
                      <div class="text-muted small zs-ellipsis2">{{ l.commande_detail.precision_lieu }}</div>
                    </td>

                    <td>
                      <div class="fw-semibold">{{ l.date_prevue || "-" }}</div>
                      <div class="text-muted small" v-if="l.date_reelle">Réelle: {{ formatDT(l.date_reelle) }}</div>
                    </td>

                    <td>
                      <span class="zs-status" :class="statusClass(l.statut)">
                        <span class="zs-status-dot"></span>
                        <i class="fa-solid me-1" :class="statusIcon(l.statut)"></i>
                        {{ labelStatut(l.statut) }}
                      </span>
                    </td>

                    <td class="text-end">
                      <div class="d-inline-flex gap-2 zs-actions">
                        <button class="btn btn-sm btn-outline-secondary zs-btn zs-btn-neo" @click="openHistory(l)" title="Historique">
                          <i class="fa-solid fa-clock-rotate-left"></i>
                        </button>

                        <button class="btn btn-sm btn-outline-primary zs-btn zs-btn-neo" @click="act('EN_LIVRAISON', l)" :disabled="loading || isFinal(l.statut)" title="Mettre en livraison">
                          <i class="fa-solid fa-truck"></i>
                        </button>

                        <button class="btn btn-sm btn-outline-success zs-btn zs-btn-neo" @click="act('LIVREE', l)" :disabled="loading || isFinal(l.statut)" title="Marquer livrée">
                          <i class="fa-solid fa-circle-check"></i>
                        </button>

                        <button class="btn btn-sm btn-outline-warning zs-btn zs-btn-neo" @click="openModal('REPORTEE', l)" :disabled="loading || isFinal(l.statut)" title="Reporter">
                          <i class="fa-solid fa-calendar-days"></i>
                        </button>

                        <button class="btn btn-sm btn-outline-danger zs-btn zs-btn-neo" @click="openModal('ANNULEE', l)" :disabled="loading || isFinal(l.statut)" title="Annuler">
                          <i class="fa-solid fa-ban"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="zs-panel-foot border-top">
              <div class="small text-muted">Total: {{ total }}</div>
              <div class="d-flex gap-2">
                <button class="btn btn-sm btn-outline-secondary zs-btn zs-btn-neo" @click="prev" :disabled="!prevUrl || loading">
                  <i class="fa-solid fa-chevron-left me-1"></i> Précédent
                </button>
                <button class="btn btn-sm btn-outline-secondary zs-btn zs-btn-neo" @click="next" :disabled="!nextUrl || loading">
                  Suivant <i class="fa-solid fa-chevron-right ms-1"></i>
                </button>
              </div>
            </div>

          </div>
        </div>
      </div>

    </div>

    <!-- Modal Action -->
    <div class="modal fade" id="actionModal" tabindex="-1" aria-hidden="true" ref="actionModalEl">
      <div class="modal-dialog">
        <div class="modal-content zs-modal">
          <div class="modal-header">
            <h5 class="modal-title">{{ modalTitle }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fermer"></button>
          </div>
          <div class="modal-body">
            <div class="mb-2">
              <label class="form-label small text-muted mb-1">Raison</label>
              <input v-model="actionPayload.raison" class="form-control form-control-sm zs-input" placeholder="Ex: client absent..." />
            </div>

            <div class="mb-2" v-if="modalAction==='REPORTEE'">
              <label class="form-label small text-muted mb-1">Nouvelle date prévue</label>
              <input v-model="actionPayload.date_prevue" type="date" class="form-control form-control-sm zs-input" />
            </div>

            <div>
              <label class="form-label small text-muted mb-1">Commentaire</label>
              <textarea v-model="actionPayload.commentaire" class="form-control form-control-sm zs-input" rows="3"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline-secondary zs-btn zs-btn-neo" data-bs-dismiss="modal">Fermer</button>
            <button class="btn btn-primary zs-btn zs-btn-neo" @click="confirmModal" :disabled="loading">
              <i class="fa-solid fa-check me-1"></i> Confirmer
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal History -->
    <div class="modal fade" id="historyModal" tabindex="-1" aria-hidden="true" ref="historyModalEl">
      <div class="modal-dialog modal-lg">
        <div class="modal-content zs-modal">
          <div class="modal-header">
            <h5 class="modal-title">Historique</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fermer"></button>
          </div>
          <div class="modal-body">
            <div v-if="!historyTarget" class="text-muted">Aucune sélection.</div>
            <div v-else>
              <div class="mb-2">
                <div class="fw-semibold">
                  Livraison L{{ historyTarget.id }} — Cmd #{{ historyTarget.commande_detail.id }}
                </div>
                <div class="text-muted small">
                  {{ historyTarget.commande_detail.client_nom }} — {{ historyTarget.commande_detail.client_contact }}
                </div>
              </div>

              <div v-if="historyTarget.events.length===0" class="text-muted">Aucun événement.</div>

              <div v-else class="table-responsive zs-table-wrap">
                <table class="table table-sm align-middle mb-0 zs-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Statut</th>
                      <th>Message</th>
                      <th>Acteur</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="e in historyTarget.events" :key="e.id">
                      <td>{{ formatDT(e.created_at) }}</td>
                      <td class="text-nowrap">{{ e.from_statut }} → {{ e.to_statut }}</td>
                      <td>{{ e.message }}</td>
                      <td>{{ e.actor_name || "-" }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline-secondary zs-btn zs-btn-neo" data-bs-dismiss="modal">Fermer</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { useConflivraisonView } from "@/views/conflivraison/assets/js/useConflivraisonView";

const {
  loading, error,

  loadingCmd, commandes, totalCmd, nextCmdUrl, prevCmdUrl, programmationDates,
  nextCmd, prevCmd, programmer,

  items, total, nextUrl, prevUrl,
  filters, showFilters, hasActiveFilters,
  toggleFilters, resetFilters,
  applyFilters, next, prev,
  refreshAll, sync,

  isFinal, labelStatut, statusClass, statusIcon, formatDT,

  actionModalEl, historyModalEl,
  modalTitle, modalAction,
  actionPayload, historyTarget,
  openModal, confirmModal, act, openHistory,
} = useConflivraisonView();
</script>

<style scoped src="@/views/conflivraison/assets/css/ConflivraisonView.css"></style>
