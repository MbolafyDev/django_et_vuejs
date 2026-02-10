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
              <h4 class="mb-0 zs-title">Encaissement</h4>
              <span class="zs-pill-soft">
                <i class="fa-solid fa-cash-register me-1"></i> Paiements & Statuts
              </span>
            </div>

            <div class="text-muted small mt-1">
              Liste des commandes • encaisser • annuler paiement • filtrage rapide
            </div>

            <!-- KPIs -->
            <div class="zs-kpis mt-3">
              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-list-check"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Résultats</div>
                  <div class="zs-kpi-value">{{ count }}</div>
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
                <div class="zs-kpi-icon"><i class="fa-solid fa-layer-group"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Page</div>
                  <div class="zs-kpi-value">{{ page }}</div>
                </div>
              </div>

              <div class="zs-kpi">
                <div class="zs-kpi-icon"><i class="fa-solid fa-gauge-high"></i></div>
                <div class="zs-kpi-body">
                  <div class="zs-kpi-label">Taille</div>
                  <div class="zs-kpi-value">{{ pageSize }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- actions -->
          <div class="d-flex gap-2 flex-wrap align-items-center">
            <button class="btn btn-primary zs-btn zs-btn-neo" @click="goPending">
              <i class="fa-solid fa-cash-register me-1"></i>
              Encaisser une commande
            </button>

            <button class="btn btn-outline-secondary zs-btn zs-btn-neo" @click="load" :disabled="loading" title="Rafraîchir">
              <i class="fa-solid fa-rotate"></i>
              <span class="ms-2 d-none d-sm-inline">Rafraîchir</span>
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

      <!-- FILTERS -->
      <div v-if="showFilters" class="zs-panel mb-3">
        <div class="zs-panel-head">
          <div class="fw-bold">
            <i class="fa-solid fa-sliders me-2 text-primary"></i> Filtres
          </div>
        </div>
        <div class="zs-panel-body">
          <div class="row g-2 align-items-end">
            <div class="col-12 col-md-4">
              <label class="form-label small text-muted mb-1">Recherche</label>
              <input
                v-model="q"
                class="form-control form-control-sm zs-input"
                placeholder="Client / contact / id..."
                @keyup.enter="applyFilters"
              />
            </div>

            <div class="col-12 col-md-4">
              <label class="form-label small text-muted mb-1">Statut paiement</label>
              <select v-model="paiement_statut" class="form-select form-select-sm zs-input">
                <option value="">Tous</option>
                <option value="EN_ATTENTE">En attente</option>
                <option value="PAYEE">Payée</option>
                <option value="ANNULEE">Annulée</option>
              </select>
            </div>

            <div class="col-12 col-md-4 d-flex gap-2">
              <button class="btn btn-sm btn-primary zs-btn zs-btn-neo" @click="applyFilters" :disabled="loading">
                <i class="fa-solid fa-magnifying-glass me-1"></i> Appliquer
              </button>
              <button class="btn btn-sm btn-outline-secondary zs-btn zs-btn-neo" @click="resetFilters" :disabled="loading">
                Réinitialiser
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- LIST PANEL -->
      <div class="zs-panel">
        <div class="zs-panel-head d-flex justify-content-between align-items-center flex-wrap gap-2">
          <div class="d-flex align-items-center gap-2 min-width-0">
            <i class="fa-solid fa-list me-1 text-primary"></i>
            <span class="fw-bold">Commandes</span>
            <span class="zs-pill-count">{{ count }}</span>
          </div>

          <div class="d-flex align-items-center gap-2">
            <select v-model.number="pageSize" class="form-select form-select-sm zs-input" style="width: 96px;" title="Taille page" @change="onPageSizeChange">
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </div>
        </div>

        <div class="zs-panel-body p-0">
          <div v-if="loading" class="p-3 text-muted">Chargement...</div>

          <div v-else class="zs-list">
            <div class="zs-list-head">
              <div class="zs-h-id">#</div>
              <div class="zs-h-client">Client</div>
              <div class="zs-h-contact">Contact</div>
              <div class="zs-h-total">Total</div>
              <div class="zs-h-liv">Livraison</div>
              <div class="zs-h-pay">Paiement</div>
              <div class="zs-h-mode">Mode</div>
              <div class="zs-h-ref">Réf.</div>
              <div class="zs-h-actions"></div>
            </div>

            <div v-if="rows.length === 0" class="text-center text-muted py-4">
              <i class="fa-solid fa-circle-info me-1"></i> Aucune commande
            </div>

            <div v-else class="zs-list-body">
              <div v-for="c in rows" :key="c.id" class="zs-row">
                <div class="zs-cell zs-id fw-bold">#{{ c.id }}</div>

                <div class="zs-cell zs-client">
                  <div class="fw-semibold zs-ellipsis2">{{ c.client_nom }}</div>
                </div>

                <div class="zs-cell zs-contact">
                  <div class="text-muted small zs-ellipsis2">{{ c.client_contact || "-" }}</div>
                </div>

                <div class="zs-cell zs-total text-end">
                  <div class="fw-bold">{{ money(c.total_commande) }}</div>
                </div>

                <div class="zs-cell zs-liv">
                  <div class="small">{{ c.date_livraison || "-" }}</div>
                </div>

                <div class="zs-cell zs-pay">
                  <span class="zs-status" :class="paiementClass(c.paiement_statut)">
                    <span class="zs-status-dot"></span>
                    <i class="fa-solid me-1" :class="paiementIcon(c.paiement_statut)"></i>
                    {{ paiementLabel(c.paiement_statut) }}
                  </span>
                </div>

                <div class="zs-cell zs-mode">
                  <div class="small">{{ c.paiement_mode || "-" }}</div>
                </div>

                <div class="zs-cell zs-ref">
                  <div class="small text-muted zs-ellipsis2">{{ c.paiement_reference || "-" }}</div>
                </div>

                <div class="zs-cell zs-actions text-end">
                  <div class="zs-actions">
                    <button
                      v-if="c.paiement_statut === 'EN_ATTENTE'"
                      class="btn btn-sm btn-primary zs-btn zs-btn-neo"
                      @click="goEncaisser(c.id)"
                    >
                      <i class="fa-solid fa-cash-register me-1"></i> Encaisser
                    </button>

                    <button
                      v-if="c.paiement_statut === 'EN_ATTENTE'"
                      class="btn btn-sm btn-outline-danger zs-btn zs-btn-neo"
                      @click="annuler(c.id)"
                      :disabled="loading"
                    >
                      <i class="fa-solid fa-ban me-1"></i> Annuler
                    </button>
                  </div>
                </div>

                <!-- ✅ sub line (MOBILE ONLY) -->
                <div class="zs-sub">
                  <div class="zs-subitem">
                    <div class="zs-subkey"><i class="fa-solid fa-user me-1"></i> Client</div>
                    <div class="zs-subval">
                      <div class="fw-semibold zs-ellipsis2">{{ c.client_nom }}</div>
                      <div class="small text-muted zs-ellipsis2">{{ c.client_contact || "-" }}</div>
                    </div>
                  </div>

                  <div class="zs-subitem">
                    <div class="zs-subkey"><i class="fa-solid fa-coins me-1"></i> Total</div>
                    <div class="zs-subval fw-bold">{{ money(c.total_commande) }}</div>
                  </div>

                  <div class="zs-subitem">
                    <div class="zs-subkey"><i class="fa-solid fa-credit-card me-1"></i> Paiement</div>
                    <div class="zs-subval">
                      <span class="zs-status" :class="paiementClass(c.paiement_statut)">
                        <span class="zs-status-dot"></span>
                        {{ paiementLabel(c.paiement_statut) }}
                      </span>
                    </div>
                  </div>

                  <div class="zs-subitem">
                    <div class="zs-subkey"><i class="fa-solid fa-receipt me-1"></i> Référence</div>
                    <div class="zs-subval small text-muted zs-ellipsis2">{{ c.paiement_reference || "-" }}</div>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>

        <div class="zs-panel-foot border-top">
          <div class="small text-muted">
            Total: {{ count }} • Page: {{ page }}
          </div>

          <div class="d-flex gap-2">
            <button class="btn btn-sm btn-outline-secondary zs-btn zs-btn-neo" :disabled="page <= 1 || loading" @click="prevPage">
              <i class="fa-solid fa-chevron-left me-1"></i> Précédent
            </button>

            <button class="btn btn-sm btn-outline-secondary zs-btn zs-btn-neo" :disabled="!hasNext || loading" @click="nextPage">
              Suivant <i class="fa-solid fa-chevron-right ms-1"></i>
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import AppNavbar from "@/components/AppNavbar.vue";
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { EncaissementAPI, type EncaissementCommande } from "@/services/encaissement";

const router = useRouter();
const loading = ref(false);

const rows = ref<EncaissementCommande[]>([]);
const count = ref(0);

const paiement_statut = ref<string>("");
const q = ref<string>("");

const page = ref(1);
const pageSize = ref(20);

const showFilters = ref(false);
function toggleFilters(){ showFilters.value = !showFilters.value; }

const hasActiveFilters = computed(() => !!(paiement_statut.value || q.value.trim()));
const hasNext = computed(() => page.value * pageSize.value < count.value);

function money(v: number) {
  try { return new Intl.NumberFormat("fr-FR").format(v) + " Ar"; }
  catch { return `${v} Ar`; }
}

function paiementLabel(s: any){
  if (s === "PAYEE") return "Payée";
  if (s === "ANNULEE") return "Annulée";
  return "En attente";
}

function paiementClass(s: any){
  if (s === "PAYEE") return "zs-st zs-st-done";
  if (s === "ANNULEE") return "zs-st zs-st-cancel";
  return "zs-st zs-st-ship";
}

function paiementIcon(s: any){
  if (s === "PAYEE") return "fa-circle-check";
  if (s === "ANNULEE") return "fa-circle-xmark";
  return "fa-hourglass-half";
}

function goEncaisser(id: number) {
  router.push({ name: "encaissement_encaisser", params: { id } });
}

function goPending() {
  paiement_statut.value = "EN_ATTENTE";
  page.value = 1;
  load();
}

function resetFilters() {
  paiement_statut.value = "";
  q.value = "";
  page.value = 1;
  load();
}

function applyFilters() {
  page.value = 1;
  load();
}

function nextPage() {
  if (!hasNext.value) return;
  page.value += 1;
  load();
}

function prevPage() {
  if (page.value <= 1) return;
  page.value -= 1;
  load();
}

function onPageSizeChange(){
  page.value = 1;
  load();
}

async function annuler(id: number) {
  if (!confirm("Annuler le paiement de cette commande ?")) return;
  loading.value = true;
  try {
    await EncaissementAPI.annulerPaiement(id, { note: "Annulation depuis l'écran encaissement." });
    await load();
  } finally {
    loading.value = false;
  }
}

async function load() {
  loading.value = true;
  try {
    const params: any = {
      paiement_statut: paiement_statut.value || undefined,
      q: q.value || undefined,
      page: page.value,
      page_size: pageSize.value,
    };

    const res = await EncaissementAPI.listCommandes(params);
    const data = res.data as any;

    rows.value = data.results || [];
    count.value = data.count || 0;
  } finally {
    loading.value = false;
  }
}

load();
</script>

<style scoped>
.min-width-0{ min-width:0; }

.zs-dot-mini{
  width: 8px; height: 8px;
  border-radius: 999px;
  background: rgba(13,110,253,1);
  box-shadow: 0 0 0 4px rgba(13,110,253,.12);
}

/* ✅ mapping colonnes */
.zs-list-head{
  grid-template-columns: 90px 1.2fr 1fr 160px 140px 170px 140px 1.2fr 240px !important;
}
.zs-row{
  grid-template-columns: 90px 1.2fr 1fr 160px 140px 170px 140px 1.2fr 240px !important;
}

.zs-h-id{ grid-column: 1; }
.zs-h-client{ grid-column: 2; }
.zs-h-contact{ grid-column: 3; }
.zs-h-total{ grid-column: 4; }
.zs-h-liv{ grid-column: 5; }
.zs-h-pay{ grid-column: 6; }
.zs-h-mode{ grid-column: 7; }
.zs-h-ref{ grid-column: 8; }
.zs-h-actions{ grid-column: 9; }

.zs-id{ grid-column: 1; }
.zs-client{ grid-column: 2; }
.zs-contact{ grid-column: 3; }
.zs-total{ grid-column: 4; }
.zs-liv{ grid-column: 5; }
.zs-pay{ grid-column: 6; }
.zs-mode{ grid-column: 7; }
.zs-ref{ grid-column: 8; }
.zs-actions{ grid-column: 9; }

.zs-ellipsis2{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

/* ✅ FIX IMPORTANT: cacher le bloc résumé sur desktop */
.zs-sub{
  display: none;          /* ✅ desktop: pas de répétition */
}

/* ✅ mobile: on cache l'entête et on affiche le bloc résumé */
@media (max-width: 992px){
  .zs-list-head{ display:none; }
  .zs-row{
    grid-template-columns: 1fr !important;
    gap: 8px !important;
    padding: 12px 12px !important;
  }
  .zs-id,.zs-client,.zs-contact,.zs-total,.zs-liv,.zs-pay,.zs-mode,.zs-ref,.zs-actions{ grid-column:1 !important; }

  .zs-sub{
    display: grid;        /* ✅ mobile: on affiche le résumé */
    grid-column: 1 !important;
    grid-template-columns: 1fr !important;
  }
}
</style>
