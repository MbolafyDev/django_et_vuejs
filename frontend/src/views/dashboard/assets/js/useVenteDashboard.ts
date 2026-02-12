import { computed, onBeforeUnmount, onMounted, ref } from "vue";
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

type Filters = {
  date_from: string;
  date_to: string;
  page: string | number;
};

export function useVenteDashboard() {
  const loading = ref(false);
  const error = ref<string | null>(null);

  const filters = ref<Filters>({
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

        DashboardAPI.articlesSortants({ ...params, limit: 12 }),
        DashboardAPI.articlesEntrants({ ...params, limit: 12 }),
      ]);

      overview.value = ov;
      sortants.value = so.items || [];
      entrants.value = en.items || [];

      destroyCharts();

      // CA line
      if (caCanvas.value) {
        const labels = ca.points.map((p: any) => p.x);
        const data = ca.points.map((p: any) => p.y);

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
        const labels = st.items.map((i: any) => i.statut);
        const data = st.items.map((i: any) => i.nb);
        const c = colors(data.length);

        statutChart = new Chart(statutCanvas.value, {
          type: "bar",
          data: {
            labels,
            datasets: [{
              label: "Commandes",
              data,
              backgroundColor: c,
              borderColor: c,
              borderWidth: 1,
              borderRadius: 10,
              maxBarThickness: 44,
            }],
          },
          options: { ...baseOptions, plugins: { ...baseOptions.plugins, legend: { display: false } } },
        });
      }

      // Payment doughnut
      if (payCanvas.value) {
        const labels = pm.items.map((i: any) => i.mode || "INCONNU");
        const data = pm.items.map((i: any) => i.ca);
        const c = colors(data.length);

        payChart = new Chart(payCanvas.value, {
          type: "doughnut",
          data: {
            labels,
            datasets: [{
              label: "CA encaissé",
              data,
              backgroundColor: c,
              borderColor: "#ffffff",
              borderWidth: 3,
              hoverOffset: 6,
            }],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: true, position: "bottom" }, tooltip: { enabled: true } },
            cutout: "62%",
          },
        });
      }

      // Top articles bar
      if (topCanvas.value) {
        const labels = top.items.map((i: any) => `${i.reference} - ${i.nom_produit}`.slice(0, 28));
        const data = top.items.map((i: any) => i.ca);
        const c = colors(data.length);

        topChart = new Chart(topCanvas.value, {
          type: "bar",
          data: { labels, datasets: [{ label: "CA", data, backgroundColor: c, borderRadius: 10, maxBarThickness: 44 }] },
          options: { ...baseOptions, plugins: { ...baseOptions.plugins, legend: { display: false } } },
        });
      }

      // Page sales bar
      if (pageCanvas.value) {
        const labels = pg.items.map((i: any) => i.page_nom || "Sans page");
        const data = pg.items.map((i: any) => i.ca);
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

  return {
    loading,
    error,
    filters,

    overview,
    sortants,
    entrants,

    caCanvas,
    statutCanvas,
    payCanvas,
    topCanvas,
    pageCanvas,

    overviewRange,
    money,
    load,
  };
}
