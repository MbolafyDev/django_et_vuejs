<template>
  <div class="zs-dashboard">
    <AppNavbar />

    <div class="container py-4">
      <!-- Header -->
      <div class="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-3">
        <div>
          <h4 class="mb-0">Dashboard ventes</h4>
          <div class="text-muted small">Commandes, CA, dépenses, bénéfices, flux articles</div>
        </div>

        <div class="d-flex gap-2 align-items-end flex-wrap">
          <div>
            <label class="form-label small mb-1">Du</label>
            <input type="date" class="form-control form-control-sm" v-model="filters.date_from" />
          </div>
          <div>
            <label class="form-label small mb-1">Au</label>
            <input type="date" class="form-control form-control-sm" v-model="filters.date_to" />
          </div>
          <div style="min-width: 220px">
            <label class="form-label small mb-1">Page</label>
            <input
              type="number"
              class="form-control form-control-sm"
              v-model="filters.page"
              placeholder="ID page (optionnel)"
            />
          </div>

          <button class="btn btn-sm btn-primary" @click="load" :disabled="loading">
            <i class="fa-solid fa-rotate"></i> Actualiser
          </button>
        </div>
      </div>

      <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

      <!-- KPI -->
      <div class="row g-2 mb-3">
        <div class="col-12 col-md-3">
          <div class="zs-kpi zs-kpi-blue">
            <div class="d-flex align-items-center justify-content-between">
              <div>
                <div class="zs-kpi-label">Commandes</div>
                <div class="zs-kpi-value">{{ overview?.nb_commandes ?? 0 }}</div>
              </div>
              <div class="zs-kpi-icon">
                <i class="fa-solid fa-receipt"></i>
              </div>
            </div>
            <div class="zs-kpi-foot text-muted small">Total période</div>
          </div>
        </div>

        <div class="col-12 col-md-3">
          <div class="zs-kpi zs-kpi-green">
            <div class="d-flex align-items-center justify-content-between">
              <div>
                <div class="zs-kpi-label">CA commandes</div>
                <div class="zs-kpi-value">{{ money(overview?.ca_total_commandes ?? 0) }}</div>
              </div>
              <div class="zs-kpi-icon">
                <i class="fa-solid fa-chart-line"></i>
              </div>
            </div>
            <div class="zs-kpi-foot text-muted small">
              Panier moyen: <span class="fw-semibold">{{ money(overview?.panier_moyen ?? 0) }}</span>
            </div>
          </div>
        </div>

        <div class="col-12 col-md-3">
          <div class="zs-kpi zs-kpi-purple">
            <div class="d-flex align-items-center justify-content-between">
              <div>
                <div class="zs-kpi-label">CA encaissé</div>
                <div class="zs-kpi-value">{{ money(overview?.ca_total_encaisse ?? 0) }}</div>
              </div>
              <div class="zs-kpi-icon">
                <i class="fa-solid fa-cash-register"></i>
              </div>
            </div>
            <div class="zs-kpi-foot text-muted small">
              Panier encaissé: <span class="fw-semibold">{{ money(overview?.panier_moyen_encaisse ?? 0) }}</span>
            </div>
          </div>
        </div>

        <div class="col-12 col-md-3">
          <div class="zs-kpi zs-kpi-orange">
            <div class="d-flex align-items-center justify-content-between">
              <div>
                <div class="zs-kpi-label">Livrées / Annulées</div>
                <div class="zs-kpi-value">
                  {{ overview?.nb_livrees ?? 0 }} / {{ overview?.nb_annulees ?? 0 }}
                </div>
              </div>
              <div class="zs-kpi-icon">
                <i class="fa-solid fa-truck-fast"></i>
              </div>
            </div>
            <div class="zs-kpi-foot text-muted small">Statuts clés</div>
          </div>
        </div>

        <!-- ✅ NOUVEAU: Dépenses -->
        <div class="col-12 col-md-6">
          <div class="zs-kpi zs-kpi-red">
            <div class="d-flex align-items-center justify-content-between">
              <div>
                <div class="zs-kpi-label">Dépenses (Achats + Charges)</div>
                <div class="zs-kpi-value">{{ money(overview?.depenses_total ?? 0) }}</div>
              </div>
              <div class="zs-kpi-icon">
                <i class="fa-solid fa-money-bill-trend-up"></i>
              </div>
            </div>
            <div class="zs-kpi-foot text-muted small d-flex flex-wrap gap-3">
              <span>Achats: <span class="fw-semibold">{{ money(overview?.achats_total ?? 0) }}</span></span>
              <span>Charges: <span class="fw-semibold">{{ money(overview?.charges_total ?? 0) }}</span></span>
              <span>COGS estimé: <span class="fw-semibold">{{ money(overview?.cogs_estime ?? 0) }}</span></span>
            </div>
          </div>
        </div>

        <!-- ✅ NOUVEAU: Bénéfice -->
        <div class="col-12 col-md-6">
          <div class="zs-kpi zs-kpi-teal">
            <div class="d-flex align-items-center justify-content-between">
              <div>
                <div class="zs-kpi-label">Bénéfice estimé</div>
                <div class="zs-kpi-value">{{ money(overview?.benefice_estime ?? 0) }}</div>
              </div>
              <div class="zs-kpi-icon">
                <i class="fa-solid fa-coins"></i>
              </div>
            </div>
            <div class="zs-kpi-foot text-muted small">
              CA − COGS estimé − Charges payées
            </div>
          </div>
        </div>
      </div>

      <!-- CHARTS -->
      <div class="row g-3">
        <div class="col-12 col-lg-7">
          <div class="zs-card">
            <div class="d-flex align-items-center justify-content-between mb-2">
              <div class="fw-semibold">CA par jour</div>
              <div class="text-muted small">{{ overviewRange }}</div>
            </div>
            <div class="zs-chart-wrap">
              <canvas ref="caCanvas"></canvas>
            </div>
          </div>
        </div>

        <div class="col-12 col-lg-5">
          <div class="zs-card">
            <div class="fw-semibold mb-2">Commandes par statut</div>
            <div class="zs-chart-wrap">
              <canvas ref="statutCanvas"></canvas>
            </div>
          </div>
        </div>

        <div class="col-12 col-lg-6">
          <div class="zs-card">
            <div class="fw-semibold mb-2">Mix paiements (encaissé)</div>
            <div class="zs-chart-wrap">
              <canvas ref="payCanvas"></canvas>
            </div>
          </div>
        </div>

        <div class="col-12 col-lg-6">
          <div class="zs-card">
            <div class="fw-semibold mb-2">Top articles (CA)</div>
            <div class="zs-chart-wrap">
              <canvas ref="topCanvas"></canvas>
            </div>
          </div>
        </div>

        <div class="col-12">
          <div class="zs-card">
            <div class="fw-semibold mb-2">Ventes par page (CA)</div>
            <div class="zs-chart-wrap">
              <canvas ref="pageCanvas"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- ✅ NOUVEAU: TABLES Flux articles -->
      <div class="row g-3 mt-1">
        <div class="col-12 col-lg-6">
          <div class="zs-card">
            <div class="d-flex align-items-center justify-content-between mb-2">
              <div class="fw-semibold">Articles sortants (ventes)</div>
              <div class="text-muted small">Quantité, total, marge</div>
            </div>

            <div class="table-responsive">
              <table class="table table-sm align-middle zs-table">
                <thead>
                  <tr>
                    <th>Article</th>
                    <th class="text-end">Qté</th>
                    <th class="text-end">Vente</th>
                    <th class="text-end">Coût</th>
                    <th class="text-end">Marge</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="it in sortants" :key="it.article_id">
                    <td class="minw-220">
                      <div class="fw-semibold">{{ it.reference }}</div>
                      <div class="text-muted small text-truncate">{{ it.nom_produit }}</div>
                    </td>
                    <td class="text-end fw-semibold">{{ it.quantite }}</td>
                    <td class="text-end">{{ money(it.total_vente) }}</td>
                    <td class="text-end">{{ money(it.cout_total_estime) }}</td>
                    <td class="text-end" :class="it.marge_estime >= 0 ? 'text-success' : 'text-danger'">
                      {{ money(it.marge_estime) }}
                    </td>
                  </tr>
                  <tr v-if="!sortants.length">
                    <td colspan="5" class="text-muted small py-3 text-center">Aucune donnée</td>
                  </tr>
                </tbody>
              </table>
            </div>

          </div>
        </div>

        <div class="col-12 col-lg-6">
          <div class="zs-card">
            <div class="d-flex align-items-center justify-content-between mb-2">
              <div class="fw-semibold">Articles entrants (achats)</div>
              <div class="text-muted small">Quantité, total achat</div>
            </div>

            <div class="table-responsive">
              <table class="table table-sm align-middle zs-table">
                <thead>
                  <tr>
                    <th>Article</th>
                    <th class="text-end">Qté</th>
                    <th class="text-end">Prix achat</th>
                    <th class="text-end">Total achat</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="it in entrants" :key="it.article_id">
                    <td class="minw-220">
                      <div class="fw-semibold">{{ it.reference }}</div>
                      <div class="text-muted small text-truncate">{{ it.nom_produit }}</div>
                    </td>
                    <td class="text-end fw-semibold">{{ it.quantite }}</td>
                    <td class="text-end">{{ money(it.prix_moyen_achat) }}</td>
                    <td class="text-end">{{ money(it.total_achat) }}</td>
                  </tr>
                  <tr v-if="!entrants.length">
                    <td colspan="4" class="text-muted small py-3 text-center">Aucune donnée</td>
                  </tr>
                </tbody>
              </table>
            </div>

          </div>
        </div>
      </div>

      <div v-if="loading" class="text-muted small mt-3">
        Chargement...
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, computed } from "vue";
import AppNavbar from "@/components/AppNavbar.vue";
import {
  DashboardAPI,
  type DashboardOverview,
  type ArticleSortant,
  type ArticleEntrant,
} from "@/services/dashboard";
import {
  Chart,
  LineController, LineElement, PointElement, LinearScale, CategoryScale,
  BarController, BarElement,
  DoughnutController, ArcElement,
  Tooltip, Legend,
} from "chart.js";

Chart.register(
  LineController, LineElement, PointElement, LinearScale, CategoryScale,
  BarController, BarElement,
  DoughnutController, ArcElement,
  Tooltip, Legend
);

const loading = ref(false);
const error = ref<string | null>(null);

const filters = ref({
  date_from: "",
  date_to: "",
  page: "",
});

const overview = ref<DashboardOverview | null>(null);
const sortants = ref<ArticleSortant[]>([]);
const entrants = ref<ArticleEntrant[]>([]);

const caCanvas = ref<HTMLCanvasElement | null>(null);
const statutCanvas = ref<HTMLCanvasElement | null>(null);
const payCanvas = ref<HTMLCanvasElement | null>(null);
const topCanvas = ref<HTMLCanvasElement | null>(null);
const pageCanvas = ref<HTMLCanvasElement | null>(null);

let caChart: Chart | null = null;
let statutChart: Chart | null = null;
let payChart: Chart | null = null;
let topChart: Chart | null = null;
let pageChart: Chart | null = null;

const overviewRange = computed(() => {
  if (!overview.value?.range) return "";
  return `${overview.value.range.date_from} → ${overview.value.range.date_to}`;
});

function money(v: number) {
  return new Intl.NumberFormat("fr-FR").format(v) + " Ar";
}

function buildParams() {
  const p: any = {};
  if (filters.value.date_from) p.date_from = filters.value.date_from;
  if (filters.value.date_to) p.date_to = filters.value.date_to;
  if ((filters.value.page || "").toString().trim()) p.page = filters.value.page;
  return p;
}

function destroyCharts() {
  caChart?.destroy(); caChart = null;
  statutChart?.destroy(); statutChart = null;
  payChart?.destroy(); payChart = null;
  topChart?.destroy(); topChart = null;
  pageChart?.destroy(); pageChart = null;
}

const PALETTE = [
  "#2563eb", "#16a34a", "#f59e0b", "#ef4444", "#8b5cf6",
  "#06b6d4", "#f97316", "#0ea5e9", "#22c55e", "#a855f7",
];

function colors(n: number) {
  const out: string[] = [];
  for (let i = 0; i < n; i++) out.push(PALETTE[i % PALETTE.length]);
  return out;
}

const baseOptions: any = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: true, labels: { boxWidth: 12, boxHeight: 12, usePointStyle: true } },
    tooltip: { enabled: true, intersect: false, mode: "index" },
  },
  scales: {
    x: { grid: { display: false }, ticks: { maxRotation: 0, autoSkip: true } },
    y: { grid: { color: "rgba(15,23,42,.08)" }, ticks: { precision: 0 } },
  },
};

async function load() {
  loading.value = true;
  error.value = null;

  try {
    const params = buildParams();

    const [ov, ca, st, pm, top, pg, so, en] = await Promise.all([
      DashboardAPI.overview(params),
      DashboardAPI.caByDay(params),
      DashboardAPI.commandesByStatut(params),
      DashboardAPI.paymentMix(params),
      DashboardAPI.topArticles({ ...params, limit: 10 }),
      DashboardAPI.salesByPage(params),

      // ✅ nouveaux
      DashboardAPI.articlesSortants({ ...params, limit: 12 }),
      DashboardAPI.articlesEntrants({ ...params, limit: 12 }),
    ]);

    overview.value = ov;
    sortants.value = so.items || [];
    entrants.value = en.items || [];

    destroyCharts();

    // CA line
    if (caCanvas.value) {
      const labels = ca.points.map((p) => p.x);
      const data = ca.points.map((p) => p.y);

      caChart = new Chart(caCanvas.value, {
        type: "line",
        data: {
          labels,
          datasets: [{
            label: ca.label,
            data,
            borderColor: "#2563eb",
            backgroundColor: "rgba(37, 99, 235, .15)",
            fill: true,
            tension: 0.25,
            pointRadius: 3,
            pointHoverRadius: 5,
            borderWidth: 3,
          }],
        },
        options: { ...baseOptions, plugins: { ...baseOptions.plugins, legend: { display: true } } },
      });
    }

    // Statut bar
    if (statutCanvas.value) {
      const labels = st.items.map((i) => i.statut);
      const data = st.items.map((i) => i.nb);
      const c = colors(data.length);

      statutChart = new Chart(statutCanvas.value, {
        type: "bar",
        data: { labels, datasets: [{ label: "Commandes", data, backgroundColor: c, borderColor: c, borderWidth: 1, borderRadius: 10, maxBarThickness: 44 }] },
        options: { ...baseOptions, plugins: { ...baseOptions.plugins, legend: { display: false } } },
      });
    }

    // Payment doughnut
    if (payCanvas.value) {
      const labels = pm.items.map((i) => i.mode || "INCONNU");
      const data = pm.items.map((i) => i.ca);
      const c = colors(data.length);

      payChart = new Chart(payCanvas.value, {
        type: "doughnut",
        data: { labels, datasets: [{ label: "CA encaissé", data, backgroundColor: c, borderColor: "#ffffff", borderWidth: 3, hoverOffset: 6 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true, position: "bottom" }, tooltip: { enabled: true } }, cutout: "62%" },
      });
    }

    // Top articles bar
    if (topCanvas.value) {
      const labels = top.items.map((i) => `${i.reference} - ${i.nom_produit}`.slice(0, 28));
      const data = top.items.map((i) => i.ca);
      const c = colors(data.length);

      topChart = new Chart(topCanvas.value, {
        type: "bar",
        data: { labels, datasets: [{ label: "CA", data, backgroundColor: c, borderRadius: 10, maxBarThickness: 44 }] },
        options: { ...baseOptions, plugins: { ...baseOptions.plugins, legend: { display: false } } },
      });
    }

    // Page sales bar
    if (pageCanvas.value) {
      const labels = pg.items.map((i) => i.page_nom || "Sans page");
      const data = pg.items.map((i) => i.ca);
      const c = colors(data.length);

      pageChart = new Chart(pageCanvas.value, {
        type: "bar",
        data: { labels, datasets: [{ label: "CA", data, backgroundColor: c, borderRadius: 10, maxBarThickness: 54 }] },
        options: { ...baseOptions, plugins: { ...baseOptions.plugins, legend: { display: false } } },
      });
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || "Erreur chargement dashboard.";
  } finally {
    loading.value = false;
  }
}

onMounted(() => load());
onBeforeUnmount(() => destroyCharts());
</script>

<style scoped>
.zs-dashboard { background: #f8fafc; min-height: 100vh; }

.zs-card {
  background: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 14px;
  padding: 14px;
  box-shadow: 0 10px 28px rgba(2, 6, 23, 0.06);
}

.zs-chart-wrap { position: relative; height: 320px; }

.zs-kpi {
  background: #ffffff;
  border-radius: 14px;
  padding: 14px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 10px 28px rgba(2, 6, 23, 0.06);
  position: relative;
  overflow: hidden;
}
.zs-kpi::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 7px; }

.zs-kpi-blue::before { background: #2563eb; }
.zs-kpi-green::before { background: #16a34a; }
.zs-kpi-purple::before { background: #8b5cf6; }
.zs-kpi-orange::before { background: #f97316; }
.zs-kpi-red::before { background: #ef4444; }
.zs-kpi-teal::before { background: #06b6d4; }

.zs-kpi-label { color: #64748b; font-size: 0.86rem; }
.zs-kpi-value { font-size: 1.55rem; font-weight: 800; letter-spacing: -0.02em; color: #0f172a; }

.zs-kpi-icon {
  width: 44px; height: 44px;
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(15, 23, 42, 0.06);
  color: #0f172a;
}

.zs-kpi-foot { margin-top: 8px; }

.zs-table thead th {
  font-size: .82rem;
  color: #64748b;
  font-weight: 700;
  border-bottom: 1px solid rgba(15,23,42,.10) !important;
}
.zs-table tbody td {
  border-color: rgba(15,23,42,.06) !important;
}
.minw-220 { min-width: 220px; }

@media (max-width: 576px) {
  .zs-chart-wrap { height: 260px; }
}
</style>
