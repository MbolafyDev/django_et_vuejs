<!-- frontend/src/views/FacturesView.vue -->
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
              <h4 class="mb-0 zs-title">Facturation</h4>

              <span class="zs-pill-soft zs-pill-soft--sm">
                <i class="fa-solid fa-file-invoice-dollar me-1"></i> Proforma & Facture
              </span>
            </div>

            <div class="text-muted small mt-1">
              Proforma si non encaissé • Facture si encaissé • PDF multi-sélection
            </div>

            <!-- KPIs -->
            <div class="zs-kpis mt-3">
              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-list-check"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Résultats</div>
                  <div class="zs-kpi-value">{{ totalCount }}</div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-square-check"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Sélection</div>
                  <div class="zs-kpi-value">{{ selectedIds.length }}</div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-file-pdf"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">PDF</div>
                  <div class="zs-kpi-value">
                    <span v-if="loadingBulkPdf">...</span>
                    <span v-else>Prêt</span>
                  </div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-shield-halved"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Statut</div>
                  <div class="zs-kpi-value">
                    <span v-if="loading" class="text-muted">Chargement</span>
                    <span v-else class="text-success">OK</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- toolbar actions -->
          <div class="d-flex gap-2 flex-wrap align-items-center">
            <FacturationToolbar
              class="zs-toolbar"
              :loading="loading"
              :loadingBulkPdf="loadingBulkPdf"
              :selectedCount="selectedIds.length"
              :totalCount="commandes.length"
              :viewMode="viewMode"
              @reload="load"
              @previewSelectedPdf="previewSelectedPdf"
              @downloadSelectedPdf="downloadSelectedPdf"
              @changeView="(m:any) => (viewMode = m)"
            />
          </div>
        </div>
      </div>

      <!-- ERROR -->
      <div v-if="error" class="alert alert-danger py-2">
        <i class="fa-solid fa-triangle-exclamation me-2"></i>{{ error }}
      </div>

      <!-- PANEL -->
      <div class="zs-panel">
        <div class="zs-panel-head d-flex justify-content-between align-items-center gap-2 flex-wrap">
          <div class="d-flex align-items-center gap-2 min-width-0">
            <i class="fa-solid fa-receipt me-1 text-primary"></i>
            <span class="fw-bold">Liste des factures</span>
            <span class="zs-pill-count zs-pill-count--sm">{{ totalCount }}</span>
          </div>
        </div>

        <div class="zs-panel-body p-0">
          <div v-if="loading" class="p-3 text-muted">Chargement...</div>

          <div v-else>
            <div v-if="commandes.length === 0" class="text-center text-muted py-4">
              <i class="fa-solid fa-circle-info me-1"></i> Aucune facture / proforma.
            </div>

            <FacturationTable
              v-else
              :commandes="commandes"
              :selectedIds="selectedIds"
              :isAllSelected="isAllSelected"
              :loadingPdfId="loadingPdfId"
              :formatMoneyFn="formatMoney"
              :viewMode="viewMode"
              @update:selectedIds="(v:any) => (selectedIds = v)"
              @toggleAll="toggleAll"
              @openPdf="openPdf"
              @downloadPdf="downloadPdf"
            />
          </div>
        </div>

        <div class="zs-panel-foot border-top">
          <div class="small text-muted">
            {{ totalCount }} résultat(s) • Sélection : {{ selectedIds.length }}
          </div>

          <div class="d-flex align-items-center gap-2">
            <button class="btn btn-sm btn-outline-secondary zs-btn" @click="load" :disabled="loading">
              <i class="fa-solid fa-rotate me-1"></i> Rafraîchir
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import AppNavbar from "@/components/AppNavbar.vue";
import FacturationToolbar from "@/components/facturation/FacturationToolbar.vue";
import FacturationTable from "@/components/facturation/FacturationTable.vue";

import { useFacturation } from "@/composables/facturation/useFacturation";
import { formatMoney } from "@/utils/format";

export default defineComponent({
  name: "FacturationView",
  components: { AppNavbar, FacturationToolbar, FacturationTable },
  data() {
    const f = useFacturation();
    return {
      ...f,
      formatMoney,
      viewMode: "table" as "table" | "card",
    };
  },
  mounted() {
    this.load();
  },
});
</script>

<style scoped>
.min-width-0 { min-width: 0; }

/* Pill du titre : plus petit */
.zs-pill-soft--sm{
  padding: 0.10rem 0.42rem !important;
  font-size: 0.66rem !important;
  line-height: 1 !important;
  border-radius: 999px !important;
  white-space: nowrap;
}
.zs-pill-soft--sm i{
  font-size: 0.68rem !important;
  line-height: 1 !important;
  vertical-align: -1px;
}

/* compteur du panel : plus petit */
.zs-pill-count--sm{
  padding: 0.08rem 0.42rem !important;
  font-size: 0.66rem !important;
  line-height: 1 !important;
  border-radius: 999px !important;
}
</style>

<style>
@import "@/assets/pages/facturation.css";
</style>
