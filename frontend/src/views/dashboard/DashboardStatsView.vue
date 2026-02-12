<template>
  <div class="zs-dashboard">
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
              <div class="zs-kpi-icon"><i class="fa-solid fa-receipt"></i></div>
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
              <div class="zs-kpi-icon"><i class="fa-solid fa-chart-line"></i></div>
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
              <div class="zs-kpi-icon"><i class="fa-solid fa-cash-register"></i></div>
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
                <div class="zs-kpi-value">{{ overview?.nb_livrees ?? 0 }} / {{ overview?.nb_annulees ?? 0 }}</div>
              </div>
              <div class="zs-kpi-icon"><i class="fa-solid fa-truck-fast"></i></div>
            </div>
            <div class="zs-kpi-foot text-muted small">Statuts clés</div>
          </div>
        </div>

        <div class="col-12 col-md-6">
          <div class="zs-kpi zs-kpi-red">
            <div class="d-flex align-items-center justify-content-between">
              <div>
                <div class="zs-kpi-label">Dépenses (Achats + Charges)</div>
                <div class="zs-kpi-value">{{ money(overview?.depenses_total ?? 0) }}</div>
              </div>
              <div class="zs-kpi-icon"><i class="fa-solid fa-money-bill-trend-up"></i></div>
            </div>
            <div class="zs-kpi-foot text-muted small d-flex flex-wrap gap-3">
              <span>Achats: <span class="fw-semibold">{{ money(overview?.achats_total ?? 0) }}</span></span>
              <span>Charges: <span class="fw-semibold">{{ money(overview?.charges_total ?? 0) }}</span></span>
              <span>COGS estimé: <span class="fw-semibold">{{ money(overview?.cogs_estime ?? 0) }}</span></span>
            </div>
          </div>
        </div>

        <div class="col-12 col-md-6">
          <div class="zs-kpi zs-kpi-teal">
            <div class="d-flex align-items-center justify-content-between">
              <div>
                <div class="zs-kpi-label">Bénéfice estimé</div>
                <div class="zs-kpi-value">{{ money(overview?.benefice_estime ?? 0) }}</div>
              </div>
              <div class="zs-kpi-icon"><i class="fa-solid fa-coins"></i></div>
            </div>
            <div class="zs-kpi-foot text-muted small">CA − COGS estimé − Charges payées</div>
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
            <div class="zs-chart-wrap"><canvas ref="caCanvas"></canvas></div>
          </div>
        </div>

        <div class="col-12 col-lg-5">
          <div class="zs-card">
            <div class="fw-semibold mb-2">Commandes par statut</div>
            <div class="zs-chart-wrap"><canvas ref="statutCanvas"></canvas></div>
          </div>
        </div>

        <div class="col-12 col-lg-6">
          <div class="zs-card">
            <div class="fw-semibold mb-2">Mix paiements (encaissé)</div>
            <div class="zs-chart-wrap"><canvas ref="payCanvas"></canvas></div>
          </div>
        </div>

        <div class="col-12 col-lg-6">
          <div class="zs-card">
            <div class="fw-semibold mb-2">Top articles (CA)</div>
            <div class="zs-chart-wrap"><canvas ref="topCanvas"></canvas></div>
          </div>
        </div>

        <div class="col-12">
          <div class="zs-card">
            <div class="fw-semibold mb-2">Ventes par page (CA)</div>
            <div class="zs-chart-wrap"><canvas ref="pageCanvas"></canvas></div>
          </div>
        </div>
      </div>

      <!-- TABLES flux articles -->
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

      <div v-if="loading" class="text-muted small mt-3">Chargement...</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useVenteDashboard } from "@/views/dashboard/assets/js/useVenteDashboard";

const {
  loading, error, filters,
  overview, sortants, entrants,
  caCanvas, statutCanvas, payCanvas, topCanvas, pageCanvas,
  overviewRange, money, load,
} = useVenteDashboard();
</script>

<style scoped src="@/views/dashboard/assets/css/VenteDashboard.css"></style>
