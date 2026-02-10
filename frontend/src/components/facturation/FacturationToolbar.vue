<!-- src/components/facturation/FacturationToolbar.vue -->
<template>
  <div class="zs-toolbar-wrap">
    <!-- Switch view -->
    <div class="zs-view-switch">
      <button
        class="btn btn-sm zs-view-btn"
        :class="{ active: viewMode === 'table' }"
        @click="$emit('changeView', 'table')"
        type="button"
        title="Mode tableau"
      >
        <i class="fa-solid fa-table"></i>
      </button>

      <button
        class="btn btn-sm zs-view-btn"
        :class="{ active: viewMode === 'card' }"
        @click="$emit('changeView', 'card')"
        type="button"
        title="Mode cartes"
      >
        <i class="fa-solid fa-grip"></i>
      </button>
    </div>

    <button
      class="btn btn-outline-secondary zs-btn zs-btn-neo"
      @click="$emit('reload')"
      :disabled="loading"
      title="Rafraîchir"
      type="button"
    >
      <i class="fa-solid fa-rotate"></i>
    </button>

    <button
      class="btn btn-outline-dark zs-btn zs-btn-neo"
      @click="$emit('previewSelectedPdf')"
      :disabled="loading || selectedCount === 0 || loadingBulkPdf"
      title="Voir PDF sélection"
      type="button"
    >
      <i class="fa-solid fa-eye me-1"></i>
      <span v-if="loadingBulkPdf">...</span>
      <span v-else>Voir PDF</span>

      <!-- ✅ mini badge très petit -->
      <span class="zs-pill-mini ms-2" v-if="selectedCount">{{ selectedCount }}</span>
    </button>

    <button
      class="btn btn-outline-primary zs-btn zs-btn-neo"
      @click="$emit('downloadSelectedPdf')"
      :disabled="loading || selectedCount === 0 || loadingBulkPdf"
      title="Télécharger PDF sélection"
      type="button"
    >
      <i class="fa-solid fa-download me-1"></i>
      <span v-if="loadingBulkPdf">...</span>
      <span v-else>PDF</span>

      <!-- ✅ mini badge très petit -->
      <span class="zs-pill-mini ms-2" v-if="selectedCount">{{ selectedCount }}</span>
    </button>

    <!-- ❌ SUPPRIMÉ : Tout (ZIP) -->
    <!-- ❌ SUPPRIMÉ : Sélection (ZIP) -->
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
    viewMode: { type: String as PropType<"table" | "card">, required: true },
  },
  emits: ["reload", "previewSelectedPdf", "downloadSelectedPdf", "changeView"],
});
</script>

<style scoped>
.zs-toolbar-wrap{
  display:flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items:center;
}

/* ✅ Mini badge VRAIMENT petit */
.zs-pill-mini{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  min-width: 16px;
  height: 16px;
  padding: 0 6px;
  border-radius: 999px;
  background: rgba(255,255,255,.75);
  border: 1px solid rgba(0,0,0,.10);
  font-weight: 800;
  font-size: .62rem;
  line-height: 1;
}

/* Switch Table/Card */
.zs-view-switch{
  display:inline-flex;
  align-items:center;
  gap: 6px;
  padding: 4px;
  border-radius: 999px;
  background: rgba(0,0,0,.04);
  border: 1px solid rgba(0,0,0,.06);
}
.zs-view-btn{
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,.08);
  background: rgba(255,255,255,.85);
  padding: 6px 8px;
  line-height: 1;
}
.zs-view-btn i{ font-size: .9rem; }
.zs-view-btn.active{
  background: rgba(0,0,0,.9);
  color: #fff;
  border-color: rgba(0,0,0,.2);
}
</style>
