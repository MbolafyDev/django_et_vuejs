<template>
  <div class="zs-root">
    <div class="container-fluid py-4 zs-admin">
      <div class="zs-hero mb-3">
        <div class="d-flex align-items-start justify-content-between flex-wrap gap-2">
          <div class="min-width-0">
            <div class="d-flex align-items-center gap-2 flex-wrap">
              <div class="zs-dot"></div>
              <h4 class="mb-0 zs-title">Charges</h4>
              <span class="zs-pill-soft">
                <i class="fa-solid fa-coins me-1"></i> Dépenses & coûts
              </span>
            </div>
            <div class="text-muted small mt-1">Salaires livreur, carburant, emballage, commissions…</div>
          </div>

          <div class="d-flex gap-2 flex-wrap">
            <button class="btn btn-primary zs-btn" @click="openCreate">
              <i class="fa-solid fa-plus me-2"></i> Nouvelle charge
            </button>
            <button class="btn btn-outline-secondary zs-btn" @click="load" :disabled="loading">
              <i class="fa-solid fa-rotate me-2"></i> Actualiser
            </button>
          </div>
        </div>

        <div class="zs-kpis mt-3">
          <div class="zs-kpi">
            <div class="zs-kpi-icon"><i class="fa-solid fa-sack-dollar"></i></div>
            <div class="zs-kpi-body">
              <div class="zs-kpi-label">Total</div>
              <div class="zs-kpi-value">{{ totalMontant }}</div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="err" class="alert alert-danger py-2">{{ err }}</div>
      <div v-if="ok" class="alert alert-success py-2">{{ ok }}</div>

      <!-- Filters -->
      <div class="card shadow-sm zs-card mb-3">
        <div class="card-body">
          <div class="row g-2 align-items-end">
            <div class="col-12 col-md-4">
              <label class="form-label small mb-1">Recherche</label>
              <input v-model="filters.q" class="form-control" placeholder="libellé, description..." />
            </div>

            <div class="col-12 col-md-3">
              <label class="form-label small mb-1">Catégorie</label>
              <select v-model="filters.categorie" class="form-select">
                <option value="">Toutes</option>
                <option v-for="c in categories" :key="c.id" :value="String(c.id)">{{ c.nom }}</option>
              </select>
            </div>

            <div class="col-12 col-md-2">
              <label class="form-label small mb-1">Statut</label>
              <select v-model="filters.statut" class="form-select">
                <option value="">Tous</option>
                <option value="PAYEE">Payée</option>
                <option value="BROUILLON">Brouillon</option>
                <option value="ANNULEE">Annulée</option>
              </select>
            </div>

            <div class="col-6 col-md-1">
              <label class="form-label small mb-1">Du</label>
              <input v-model="filters.date_from" type="date" class="form-control" />
            </div>
            <div class="col-6 col-md-1">
              <label class="form-label small mb-1">Au</label>
              <input v-model="filters.date_to" type="date" class="form-control" />
            </div>

            <div class="col-12 col-md-1 d-grid">
              <button class="btn btn-outline-dark zs-btn" @click="load" :disabled="loading">
                <i class="fa-solid fa-filter"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Table -->
      <div class="card shadow-sm zs-card">
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Date</th>
                  <th>Catégorie</th>
                  <th>Libellé</th>
                  <th class="text-end">Montant</th>
                  <th>Statut</th>
                  <th>Mode</th>
                  <th>Commande</th>
                  <th class="text-end">Actions</th>
                </tr>
              </thead>

              <tbody>
                <tr v-if="loading">
                  <td colspan="8" class="text-center py-4 text-muted">Chargement...</td>
                </tr>
                <tr v-else-if="items.length === 0">
                  <td colspan="8" class="text-center py-4 text-muted">Aucune charge</td>
                </tr>

                <tr v-for="it in items" :key="it.id">
                  <td>{{ it.date_charge }}</td>
                  <td>{{ it.categorie_nom || it.categorie }}</td>
                  <td class="fw-semibold">{{ it.libelle }}</td>
                  <td class="text-end fw-bold">{{ Number(it.montant).toLocaleString() }}</td>
                  <td>
                    <span class="badge bg-success" v-if="it.statut === 'PAYEE'">Payée</span>
                    <span class="badge bg-secondary" v-else-if="it.statut === 'BROUILLON'">Brouillon</span>
                    <span class="badge bg-danger" v-else>Annulée</span>
                  </td>
                  <td>{{ it.mode_paiement }}</td>
                  <td>{{ it.commande ?? "—" }}</td>
                  <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary me-2" @click="openEdit(it)">
                      <i class="fa-solid fa-pen"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" @click="remove(it)">
                      <i class="fa-solid fa-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>

            </table>
          </div>
        </div>
      </div>

      <!-- Modal -->
      <div class="modal fade" tabindex="-1" ref="modalEl">
        <div class="modal-dialog modal-dialog-centered modal-lg">
          <div class="modal-content zs-modal">
            <div class="modal-header">
              <div class="fw-bold">
                <i class="fa-solid fa-coins me-2 text-primary"></i>
                {{ editingId ? "Modifier une charge" : "Nouvelle charge" }}
              </div>
              <button type="button" class="btn-close" @click="/* modal instance gérée par composable */ null"></button>
            </div>

            <div class="modal-body">
              <div v-if="err" class="alert alert-danger py-2">{{ err }}</div>

              <div class="row g-2">
                <div class="col-12 col-md-4">
                  <label class="form-label">Date</label>
                  <input v-model="form.date_charge" type="date" class="form-control" />
                </div>

                <div class="col-12 col-md-4">
                  <label class="form-label">Catégorie</label>
                  <select v-model="form.categorie" class="form-select">
                    <option value="">—</option>
                    <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.nom }}</option>
                  </select>
                </div>

                <div class="col-12 col-md-4">
                  <label class="form-label">Statut</label>
                  <select v-model="form.statut" class="form-select">
                    <option value="PAYEE">Payée</option>
                    <option value="BROUILLON">Brouillon</option>
                    <option value="ANNULEE">Annulée</option>
                  </select>
                </div>

                <div class="col-12">
                  <label class="form-label">Libellé</label>
                  <input v-model="form.libelle" class="form-control" placeholder="Ex: Salaire livreur" />
                </div>

                <div class="col-12">
                  <label class="form-label">Description</label>
                  <textarea v-model="form.description" class="form-control" rows="3"></textarea>
                </div>

                <div class="col-12 col-md-4">
                  <label class="form-label">Montant</label>
                  <input v-model="form.montant" class="form-control" placeholder="Ex: 20000" />
                </div>

                <div class="col-12 col-md-4">
                  <label class="form-label">Mode paiement</label>
                  <select v-model="form.mode_paiement" class="form-select">
                    <option value="CASH">Cash</option>
                    <option value="MVOLA">MVola</option>
                    <option value="ORANGE_MONEY">Orange Money</option>
                    <option value="VISA">VISA</option>
                    <option value="AUTRE">Autre</option>
                  </select>
                </div>

                <div class="col-12 col-md-4">
                  <label class="form-label">Commande (optionnel)</label>
                  <input v-model="form.commande" class="form-control" placeholder="ID commande" />
                </div>

                <div class="col-12">
                  <label class="form-label">Pièce / reçu (optionnel)</label>
                  <input type="file" class="form-control" @change="onPickPiece" />
                </div>
              </div>
            </div>

            <div class="modal-footer">
              <button class="btn btn-outline-secondary zs-btn" type="button" data-bs-dismiss="modal" :disabled="saving">
                Annuler
              </button>
              <button class="btn btn-primary zs-btn" @click="save" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="fa-solid fa-floppy-disk me-2"></i>
                Enregistrer
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { useChargesView } from "@/views/charge/assets/js/useChargesView";

const {
  loading, saving, err, ok,
  items, categories, filters,
  modalEl, editingId, form,
  totalMontant,
  openCreate, openEdit,
  onPickPiece,
  load, save, remove,
} = useChargesView();
</script>

<style scoped src="@/views/charge/assets/css/ChargesView.css"></style>
