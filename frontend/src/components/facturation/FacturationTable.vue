<!-- src/components/facturation/FacturationTable.vue -->
<template>
  <div class="zs-list">
    <!-- head -->
    <div class="zs-list-head">
      <div class="zs-h-check">
        <input type="checkbox" :checked="isAllSelected" @change="onToggleAll($event)" />
      </div>
      <div class="zs-h-num">N°</div>
      <div class="zs-h-type">Type</div>
      <div class="zs-h-cmd">Commande</div>
      <div class="zs-h-client">Client</div>
      <div class="zs-h-total">Total</div>
      <div class="zs-h-pay">Paiement</div>
      <div class="zs-h-actions"></div>
    </div>

    <div v-if="!commandes.length" class="text-center text-muted py-4">
      <i class="fa-solid fa-circle-info me-1"></i> Aucun résultat
    </div>

    <div v-else class="zs-list-body">
      <div v-for="c in commandes" :key="c.id" class="zs-row">
        <!-- check -->
        <div class="zs-cell zs-check">
          <input type="checkbox" :value="c.id" v-model="localSelectedIds" />
        </div>

        <!-- numero -->
        <div class="zs-cell zs-num fw-bold">
          {{ c.numero_affiche }}
        </div>

        <!-- type -->
        <div class="zs-cell zs-type">
          <span class="zs-status" :class="factureTypeClass(c.type_facture)">
            <span class="zs-status-dot"></span>
            <i class="fa-solid me-1" :class="c.type_facture === 'FACTURE' ? 'fa-circle-check' : 'fa-file-lines'"></i>
            {{ c.type_facture }}
          </span>
        </div>

        <!-- commande -->
        <div class="zs-cell zs-cmd">
          <div class="fw-semibold">#{{ c.id }}</div>
          <div class="small text-muted">Commande</div>
        </div>

        <!-- client -->
        <div class="zs-cell zs-client">
          <div class="fw-semibold zs-ellipsis2">{{ c.commande_detail?.client_nom || "-" }}</div>
          <div class="small text-muted zs-ellipsis2">Page: {{ c.commande_detail?.page_detail?.nom || "-" }}</div>
        </div>

        <!-- total -->
        <div class="zs-cell zs-total text-end">
          <div class="fw-bold">{{ formatMoneyFn(c.commande_detail?.total_commande || 0) }}</div>
          <div class="small text-muted">
            Cmd #{{ c.commande_detail?.id || "-" }}
          </div>
        </div>

        <!-- paiement -->
        <div class="zs-cell zs-pay">
          <span class="zs-status" :class="paiementClass(c.paiement_statut)">
            <span class="zs-status-dot"></span>
            <i class="fa-solid me-1" :class="paiementIcon(c.paiement_statut)"></i>
            {{ c.paiement_statut }}
          </span>
        </div>

        <!-- actions -->
        <div class="zs-cell zs-actions text-end">
          <div class="zs-actions">
            <button
              class="btn btn-sm btn-outline-secondary zs-btn"
              @click="$emit('openPdf', c.id)"
              :disabled="loadingPdfId === c.id"
            >
              <i class="fa-solid fa-eye"></i>
              <span v-if="loadingPdfId === c.id" class="ms-1">...</span>
              <span v-else class="ms-1">Voir</span>
            </button>

            <button
              class="btn btn-sm btn-outline-primary zs-btn"
              @click="$emit('downloadPdf', c.id, c.numero_affiche)"
              :disabled="loadingPdfId === c.id"
            >
              <i class="fa-solid fa-download"></i>
              <span class="ms-1">PDF</span>
            </button>
          </div>
        </div>

        <!-- ✅ sub (MOBILE ONLY) : affiché uniquement sur mobile via CSS -->
        <div class="zs-sub">
          <div class="zs-subitem">
            <div class="zs-subkey"><i class="fa-regular fa-window-maximize me-1"></i> Page</div>
            <div class="zs-subval d-flex align-items-center gap-2 min-width-0">
              <img v-if="c.logo_url" :src="c.logo_url" class="facturation-logo" />
              <span class="zs-ellipsis2">{{ c.commande_detail?.page_detail?.nom || "-" }}</span>
            </div>
          </div>

          <div class="zs-subitem">
            <div class="zs-subkey"><i class="fa-solid fa-user me-1"></i> Client</div>
            <div class="zs-subval">
              <div class="fw-semibold zs-ellipsis2">{{ c.commande_detail?.client_nom || "-" }}</div>
              <div class="small text-muted zs-ellipsis2">{{ c.commande_detail?.client_contact || "" }}</div>
            </div>
          </div>

          <div class="zs-subitem">
            <div class="zs-subkey"><i class="fa-solid fa-coins me-1"></i> Total</div>
            <div class="zs-subval fw-bold">{{ formatMoneyFn(c.commande_detail?.total_commande || 0) }}</div>
          </div>

          <div class="zs-subitem">
            <div class="zs-subkey"><i class="fa-solid fa-credit-card me-1"></i> Paiement</div>
            <div class="zs-subval">
              <span class="zs-status" :class="paiementClass(c.paiement_statut)">
                <span class="zs-status-dot"></span>
                {{ c.paiement_statut }}
              </span>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue";
import type { CommandeFacturationRow } from "@/services/facturation";

export default defineComponent({
  name: "FacturationTable",
  props: {
    commandes: { type: Array as PropType<CommandeFacturationRow[]>, required: true },
    selectedIds: { type: Array as PropType<number[]>, required: true },
    isAllSelected: { type: Boolean as PropType<boolean>, required: true },
    loadingPdfId: { type: Number as PropType<number | null>, required: true },
    formatMoneyFn: { type: Function as PropType<(n: number) => string>, required: true },
  },
  emits: ["update:selectedIds", "toggleAll", "openPdf", "downloadPdf"],
  computed: {
    localSelectedIds: {
      get(): number[] {
        return this.selectedIds;
      },
      set(v: number[]) {
        this.$emit("update:selectedIds", v);
      },
    },
  },
  methods: {
    onToggleAll(e: any) {
      const checked = !!e.target.checked;
      this.$emit("toggleAll", checked);
    },
    factureTypeClass(t: any) {
      return t === "FACTURE" ? "zs-st zs-st-done" : "zs-st zs-st-ship";
    },
    paiementClass(s: any) {
      if (s === "PAYEE") return "zs-st zs-st-done";
      if (s === "ANNULEE") return "zs-st zs-st-neutral";
      return "zs-st zs-st-ship";
    },
    paiementIcon(s: any) {
      if (s === "PAYEE") return "fa-circle-check";
      if (s === "ANNULEE") return "fa-circle-xmark";
      return "fa-hourglass-half";
    },
  },
});
</script>

<style scoped>
/* ✅ IMPORTANT : par défaut (desktop) => PAS de sub (sinon doublon) */
.zs-sub{ display: none; }

/* mobile */
@media (max-width: 992px){
  .zs-list-head{ display:none; }

  .zs-row{
    grid-template-columns: 1fr !important;
    gap: 8px !important;
    padding: 12px 12px !important;
  }

  .zs-check,.zs-num,.zs-type,.zs-cmd,.zs-client,.zs-total,.zs-pay,.zs-actions{
    grid-column: 1 !important;
  }

  /* ✅ sur mobile, on affiche la subline */
  .zs-sub{
    display: grid;
    grid-column: 1 !important;
    grid-template-columns: 1fr !important;
  }
}
</style>

