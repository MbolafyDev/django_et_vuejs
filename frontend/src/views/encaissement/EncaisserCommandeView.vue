<template>
  <div class="zs-admin">
    <div class="container-fluid py-4">
      <!-- HERO -->
      <div class="zs-hero mb-3 enc-wrap">
        <div class="d-flex align-items-start justify-content-between flex-wrap gap-3">
          <div class="min-width-0">
            <div class="d-flex align-items-center gap-2 flex-wrap">
              <div class="zs-dot"></div>
              <h4 class="mb-0 zs-title">Encaisser commande</h4>

              <span class="zs-pill-soft zs-pill-soft--sm">
                <i class="fa-solid fa-check-to-slot me-1"></i> Validation paiement
              </span>
            </div>
            <div class="text-muted small mt-1">
              Commande <b>#{{ id }}</b> • Choisir mode • Saisir référence si besoin
            </div>
          </div>

          <div class="d-flex gap-2 flex-wrap align-items-center">
            <button class="btn btn-outline-secondary zs-btn zs-btn-neo" @click="back">
              <i class="fa-solid fa-arrow-left me-1"></i> Retour
            </button>
          </div>
        </div>
      </div>

      <!-- PANEL -->
      <div class="zs-panel enc-wrap">
        <div class="zs-panel-head d-flex justify-content-between align-items-center flex-wrap gap-2">
          <div class="fw-bold">
            <i class="fa-solid fa-cash-register me-2 text-primary"></i>
            Encaisser #{{ id }}
          </div>

          <span v-if="commande" class="zs-status zs-st zs-st-ship zs-status--table">
            <span class="zs-status-dot"></span>
            <i class="fa-solid fa-hourglass-half me-1"></i>
            EN ATTENTE
          </span>
        </div>

        <div class="zs-panel-body">
          <div v-if="loading" class="text-muted">Chargement...</div>

          <div v-else>
            <div class="row g-3">
              <div class="col-12 col-md-7">
                <div class="zs-kpi w-100 kpi-unset">
                  <div class="zs-kpi-icon"><i class="fa-solid fa-user"></i></div>
                  <div class="zs-kpi-body min-width-0">
                    <div class="zs-kpi-label">Client</div>
                    <div class="zs-kpi-value kpi-name">
                      <span class="zs-ellipsis2">{{ commande?.client_nom }}</span>
                    </div>
                    <div class="small text-muted zs-ellipsis2">{{ commande?.client_contact }}</div>
                  </div>
                </div>
              </div>

              <div class="col-12 col-md-5">
                <div class="zs-kpi w-100 kpi-unset">
                  <div class="zs-kpi-icon"><i class="fa-solid fa-coins"></i></div>
                  <div class="zs-kpi-body">
                    <div class="zs-kpi-label">Total à payer</div>
                    <div class="zs-kpi-value">{{ money(commande?.total_commande || 0) }}</div>
                  </div>
                </div>
              </div>
            </div>

            <hr class="my-3" />

            <div class="row g-3">
              <div class="col-12 col-md-6">
                <label class="form-label small text-muted mb-1">Mode de paiement</label>
                <div class="input-group">
                  <span class="input-group-text zs-ig"><i class="fa-solid fa-credit-card"></i></span>
                  <select v-model="mode" class="form-select zs-input">
                    <option value="ESPECE">Espèce</option>
                    <option value="MVOLA">MVola</option>
                    <option value="ORANGE_MONEY">Orange Money</option>
                  </select>
                </div>
              </div>

              <div class="col-12 col-md-6" v-if="mode !== 'ESPECE'">
                <label class="form-label small text-muted mb-1">Référence paiement</label>
                <div class="input-group">
                  <span class="input-group-text zs-ig"><i class="fa-solid fa-hashtag"></i></span>
                  <input v-model="reference" class="form-control zs-input" placeholder="Ex: TXN123..." />
                </div>
                <div v-if="errorRef" class="text-danger small mt-1">{{ errorRef }}</div>
              </div>

              <div class="col-12">
                <label class="form-label small text-muted mb-1">Note (optionnel)</label>
                <textarea v-model="note" class="form-control zs-input" rows="2" placeholder="Ex: reçu par ..."></textarea>
              </div>
            </div>

            <div class="d-flex justify-content-end gap-2 mt-3">
              <button class="btn btn-outline-secondary zs-btn zs-btn-neo" @click="back" :disabled="submitting">
                Annuler
              </button>
              <button class="btn btn-primary zs-btn zs-btn-neo" :disabled="submitting" @click="submit">
                <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="fa-solid fa-check me-1"></i>
                Valider encaissement
              </button>
            </div>

            <div v-if="error" class="alert alert-danger mt-3">
              <i class="fa-solid fa-triangle-exclamation me-2"></i>{{ error }}
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { useEncaisserCommande } from "@/views/encaissement/assets/js/useEncaisserCommande";

const {
  id,
  loading,
  submitting,
  commande,
  mode,
  reference,
  note,
  error,
  errorRef,
  money,
  back,
  submit,
} = useEncaisserCommande();
</script>

<style scoped src="@/views/encaissement/assets/css/EncaisserCommandeView.css"></style>
