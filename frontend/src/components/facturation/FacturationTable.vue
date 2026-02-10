<!-- src/components/facturation/FacturationTable.vue -->
<template>
  <div class="zs-list">
    <!-- ====== MODE TABLE ====== -->
    <template v-if="viewMode === 'table'">
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
          <div class="zs-cell zs-check">
            <input type="checkbox" :value="c.id" v-model="localSelectedIds" />
          </div>

          <div class="zs-cell zs-num fw-bold">
            {{ c.numero_affiche }}
          </div>

          <!-- ✅ BADGE TABLE: plus petit -->
          <div class="zs-cell zs-type">
            <span class="zs-status zs-status--table" :class="factureTypeClass(c.type_facture)">
              <span class="zs-status-dot"></span>
              <i class="fa-solid me-1" :class="c.type_facture === 'FACTURE' ? 'fa-circle-check' : 'fa-file-lines'"></i>
              {{ c.type_facture }}
            </span>
          </div>

          <div class="zs-cell zs-cmd">
            <div class="fw-semibold">#{{ c.id }}</div>
            <div class="small text-muted">Commande</div>
          </div>

          <div class="zs-cell zs-client">
            <div class="fw-semibold zs-ellipsis2">{{ c.commande_detail?.client_nom || "-" }}</div>
            <div class="small text-muted zs-ellipsis2">Page: {{ c.commande_detail?.page_detail?.nom || "-" }}</div>
          </div>

          <div class="zs-cell zs-total text-end">
            <div class="fw-bold">{{ formatMoneyFn(c.commande_detail?.total_commande || 0) }}</div>
            <div class="small text-muted">Cmd #{{ c.commande_detail?.id || "-" }}</div>
          </div>

          <!-- ✅ BADGE TABLE: plus petit -->
          <div class="zs-cell zs-pay">
            <span class="zs-status zs-status--table" :class="paiementClass(c.paiement_statut)">
              <span class="zs-status-dot"></span>
              <i class="fa-solid me-1" :class="paiementIcon(c.paiement_statut)"></i>
              {{ c.paiement_statut }}
            </span>
          </div>

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

          <!-- Mobile sub (comme avant) -->
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
                <!-- ici aussi on peut le réduire -->
                <span class="zs-status zs-status--table" :class="paiementClass(c.paiement_statut)">
                  <span class="zs-status-dot"></span>
                  {{ c.paiement_statut }}
                </span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </template>

    <!-- ====== MODE CARD ====== -->
    <template v-else>
      <div v-if="!commandes.length" class="text-center text-muted py-4">
        <i class="fa-solid fa-circle-info me-1"></i> Aucun résultat
      </div>

      <div v-else class="zs-cards">
        <div v-for="c in commandes" :key="c.id" class="zs-card">
          <div class="zs-card-top">
            <div class="d-flex align-items-center gap-2">
              <input type="checkbox" :value="c.id" v-model="localSelectedIds" />

              <div class="fw-bold">
                {{ c.numero_affiche }}
                <span class="text-muted fw-normal ms-1">• #{{ c.id }}</span>
              </div>
            </div>

            <div class="d-flex align-items-center gap-2">
              <span class="zs-status zs-card-status" :class="factureTypeClass(c.type_facture)">
                <span class="zs-status-dot"></span>
                <i class="fa-solid me-1" :class="c.type_facture === 'FACTURE' ? 'fa-circle-check' : 'fa-file-lines'"></i>
                {{ c.type_facture }}
              </span>
            </div>
          </div>

          <div class="zs-card-body">
            <div class="zs-card-row">
              <div class="zs-k">Client</div>
              <div class="zs-v fw-semibold">{{ c.commande_detail?.client_nom || "-" }}</div>
            </div>

            <div class="zs-card-row">
              <div class="zs-k">Page</div>
              <div class="zs-v d-flex align-items-center gap-2 min-width-0">
                <img v-if="c.logo_url" :src="c.logo_url" class="facturation-logo" />
                <span class="zs-ellipsis2">{{ c.commande_detail?.page_detail?.nom || "-" }}</span>
              </div>
            </div>

            <div class="zs-card-row">
              <div class="zs-k">Total</div>
              <div class="zs-v fw-bold">{{ formatMoneyFn(c.commande_detail?.total_commande || 0) }}</div>
            </div>

            <div class="zs-card-row">
              <div class="zs-k">Paiement</div>
              <div class="zs-v">
                <span class="zs-status zs-card-status" :class="paiementClass(c.paiement_statut)">
                  <span class="zs-status-dot"></span>
                  <i class="fa-solid me-1" :class="paiementIcon(c.paiement_statut)"></i>
                  {{ c.paiement_statut }}
                </span>
              </div>
            </div>
          </div>

          <div class="zs-card-actions">
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
      </div>
    </template>
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
    viewMode: { type: String as PropType<"table" | "card">, required: true },
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
/* mobile sub */
.zs-sub{ display: none; }

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

  .zs-sub{
    display: grid;
    grid-column: 1 !important;
    grid-template-columns: 1fr !important;
  }
}

/* ===== Card mode ===== */
.zs-cards{
  display:grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  padding: 12px;
}
@media (max-width: 1200px){
  .zs-cards{ grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 768px){
  .zs-cards{ grid-template-columns: 1fr; }
}

.zs-card{
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 14px;
  background: rgba(255,255,255,.85);
  box-shadow: 0 10px 30px rgba(0,0,0,.06);
  overflow:hidden;
}

.zs-card-top{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 10px;
  padding: 12px 12px 10px;
  border-bottom: 1px solid rgba(0,0,0,.06);
}

.zs-card-body{
  padding: 10px 12px 12px;
  display:grid;
  gap: 8px;
}

.zs-card-row{
  display:grid;
  grid-template-columns: 90px 1fr;
  gap: 10px;
  align-items:center;
}

.zs-k{
  font-size: .78rem;
  color: rgba(0,0,0,.55);
}
.zs-v{ min-width: 0; }

.zs-card-actions{
  display:flex;
  gap: 8px;
  justify-content:flex-end;
  padding: 10px 12px 12px;
}

/* badge statut compact dans les cards */
.zs-card-status{
  padding: 0.18rem 0.5rem !important;
  font-size: .72rem !important;
  line-height: 1 !important;
}
</style>
