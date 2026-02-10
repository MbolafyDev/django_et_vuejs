<!-- src/components/facturation/FacturationToolbar.vue -->
<template>
  <div class="zs-toolbar-wrap">
    <button class="btn btn-outline-secondary zs-btn zs-btn-neo" @click="$emit('reload')" :disabled="loading" title="Rafraîchir">
      <i class="fa-solid fa-rotate"></i>
    </button>

    <button
      class="btn btn-outline-dark zs-btn zs-btn-neo"
      @click="$emit('previewSelectedPdf')"
      :disabled="loading || selectedCount === 0 || loadingBulkPdf"
      title="Voir PDF sélection"
    >
      <i class="fa-solid fa-eye me-1"></i>
      <span v-if="loadingBulkPdf">...</span>
      <span v-else>Voir PDF</span>
      <span class="zs-pill-mini ms-2" v-if="selectedCount">{{ selectedCount }}</span>
    </button>

    <button
      class="btn btn-outline-primary zs-btn zs-btn-neo"
      @click="$emit('downloadSelectedPdf')"
      :disabled="loading || selectedCount === 0 || loadingBulkPdf"
      title="Télécharger PDF sélection"
    >
      <i class="fa-solid fa-download me-1"></i>
      <span v-if="loadingBulkPdf">...</span>
      <span v-else>PDF</span>
      <span class="zs-pill-mini ms-2" v-if="selectedCount">{{ selectedCount }}</span>
    </button>

    <button
      class="btn btn-outline-primary zs-btn zs-btn-neo"
      @click="$emit('downloadAll')"
      :disabled="loading || totalCount === 0"
      title="Tout (ZIP)"
    >
      <i class="fa-solid fa-download me-1"></i> Tout (ZIP)
    </button>

    <button
      class="btn btn-primary zs-btn zs-btn-neo"
      @click="$emit('downloadSelectedZip')"
      :disabled="loading || selectedCount === 0"
      title="Sélection (ZIP)"
    >
      <i class="fa-solid fa-file-zipper me-1"></i> Sélection (ZIP)
    </button>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue";

export default defineComponent({
  name: "FacturationToolbar",
  props: {
    loading: { type: Boolean as PropType<boolean>, required: true },
    loadingBulkPdf: { type: Boolean as PropType<boolean>, required: true },
    selectedCount: { type: Number as PropType<number>, required: true },
    totalCount: { type: Number as PropType<number>, required: true },
  },
  emits: ["reload", "previewSelectedPdf", "downloadSelectedPdf", "downloadAll", "downloadSelectedZip"],
});
</script>

<style scoped>
.zs-toolbar-wrap{
  display:flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items:center;
}
.zs-pill-mini{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  min-width: 26px;
  height: 22px;
  padding: 0 8px;
  border-radius: 999px;
  background: rgba(255,255,255,.75);
  border: 1px solid rgba(0,0,0,.08);
  font-weight: 900;
  font-size: .75rem;
}
</style>
