<!-- frontend/src/components/AppNavbar.vue -->
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick, computed } from "vue";
import { useAuthStore } from "../stores/auth";
import { useRouter, useRoute } from "vue-router";
import Tooltip from "bootstrap/js/dist/tooltip";

// ✅ import API configuration
import { ConfigurationAPI, type PageConfig } from "@/services/configuration";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const logout = async () => {
  await auth.logout();
  router.push({ name: "login" });
};

const menus = [
  { to: "/commandes", label: "Commandes", icon: "fa-solid fa-receipt" },
  { to: "/factures", label: "Facturation", icon: "fa-solid fa-file-invoice-dollar" },
  { to: "/encaissement", label: "Encaissement", icon: "fa-solid fa-cash-register" },

  // ✅ UPDATE: l’icône livraison pointe vers Conflivraison
  { to: "/conflivraison", label: "Livraison", icon: "fa-solid fa-truck-fast" },

  { to: "/achats", label: "Achat", icon: "fa-solid fa-cart-shopping" },
  { to: "/articles", label: "Articles", icon: "fa-solid fa-box" },
  { to: "/clients", label: "Clients", icon: "fa-solid fa-users" },
];

const isActive = (path: string) => route.path.startsWith(path);

/* Tooltips Bootstrap (hover seulement) */
function disposeAllTooltips() {
  document.querySelectorAll('[data-zs-tooltip="1"]').forEach((el) => {
    const instance = Tooltip.getInstance(el as Element);
    if (instance) instance.dispose();
  });
}

function initTooltipsHover() {
  disposeAllTooltips();
  document.querySelectorAll('[data-zs-tooltip="1"]').forEach((el) => {
    new Tooltip(el as Element, { placement: "bottom", trigger: "hover focus" });
  });
}

/* ===========================
   ✅ Pages dynamiques (configuration)
=========================== */
const configPages = ref<PageConfig[]>([]);
const configLoading = ref(false);

const configLinks = computed(() => {
  return (configPages.value || [])
    .filter((p) => p && p.actif && (p.lien || "").trim().length > 0)
    .sort((a, b) => (a.ordre || 0) - (b.ordre || 0));
});

function normalizeLink(link: string) {
  const l = (link || "").trim();
  if (!l) return "/";
  if (l.startsWith("http://") || l.startsWith("https://")) return l;
  return l.startsWith("/") ? l : "/" + l;
}

async function loadConfigLinks() {
  if (!auth.isAuthenticated) {
    configPages.value = [];
    return;
  }

  configLoading.value = true;
  try {
    const res = await ConfigurationAPI.listPages({ actif: true, page_size: 200 });
    const data: any = res.data;
    configPages.value = data?.results || [];
  } catch (e) {
    configPages.value = [];
  } finally {
    configLoading.value = false;
  }
}

/* ===========================
   lifecycle
=========================== */
onMounted(async () => {
  await nextTick();
  initTooltipsHover();
  await loadConfigLinks();
});

onBeforeUnmount(() => {
  disposeAllTooltips();
});

watch(
  () => route.fullPath,
  async () => {
    await nextTick();
    initTooltipsHover();
  }
);

watch(
  () => auth.isAuthenticated,
  async () => {
    await loadConfigLinks();
  }
);
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom shadow-sm">
    <div class="container-fluid">

      <!-- ✅ Logo + nom => redirect vers DashboardStatsView -->
      <router-link
        class="navbar-brand d-flex align-items-center gap-2 fw-bold"
        :to="{ name: 'dashboard-stats' }"
        aria-label="Retour au dashboard statistiques"
      >
        <img src="/logo.jpg" alt="Logo" height="32" class="zs-brand-click" />
        <span class="text-primary zs-brand-click">MBOLAFY</span>
      </router-link>

      <!-- Burger -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#mainNavbar"
        aria-controls="mainNavbar"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="mainNavbar">

        <!-- ✅ Menus centrés (desktop) -->
        <ul class="navbar-nav zs-nav-icons zs-nav-center">
          <li v-for="m in menus" :key="m.to" class="nav-item">
            <router-link
              :to="m.to"
              class="nav-link d-flex flex-column align-items-center gap-1 zs-icon-link"
              data-zs-tooltip="1"
              data-bs-placement="bottom"
              :title="m.label"
              :class="{ active: isActive(m.to) }"
            >
              <i :class="m.icon" class="zs-menu-icon" aria-hidden="true"></i>
              <span class="d-lg-none small">{{ m.label }}</span>
            </router-link>
          </li>
        </ul>

        <!-- ✅ À droite -->
        <div class="ms-lg-auto d-flex align-items-center gap-2">

          <!-- Si non connecté -->
          <template v-if="!auth.isAuthenticated">
            <router-link class="btn btn-outline-primary" to="/register">
              <i class="fa-solid fa-user-plus me-2"></i> Inscription
            </router-link>
            <router-link class="btn btn-primary" to="/login">
              <i class="fa-solid fa-right-to-bracket me-2"></i> Connexion
            </router-link>
          </template>

          <!-- Si connecté -->
          <template v-else>
            <span class="text-muted me-2 d-none d-lg-inline">{{ auth.user?.username }}</span>

            <!-- ✅ Dropdown Paramètres -->
            <div class="nav-item dropdown">
              <button
                class="btn btn-outline-primary btn-sm dropdown-toggle"
                type="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
                data-zs-tooltip="1"
                data-bs-placement="bottom"
                title="Paramètres"
              >
                <i class="fa-solid fa-gear"></i>
              </button>

              <ul class="dropdown-menu dropdown-menu-end shadow-sm" style="min-width: 280px;">

                <!-- ✅ Config dynamique -->
                <li>
                  <h6 class="dropdown-header d-flex align-items-center justify-content-between">
                    <span>Configuration</span>
                    <span v-if="configLoading" class="text-muted small">...</span>
                  </h6>
                </li>

                <li v-if="configLinks.length === 0">
                  <span class="dropdown-item-text text-muted small">
                    Aucune page de configuration.
                  </span>
                </li>

                <template v-else>
                  <li v-for="p in configLinks" :key="p.id">
                    <a
                      v-if="normalizeLink(p.lien).startsWith('http')"
                      class="dropdown-item d-flex align-items-center gap-2"
                      :href="normalizeLink(p.lien)"
                      target="_blank"
                      rel="noopener"
                    >
                      <img v-if="p.logo_url" :src="p.logo_url" class="zs-dd-logo" alt="" />
                      <i v-else class="fa-solid fa-link text-muted"></i>
                      <span>{{ p.nom }}</span>
                      <i class="fa-solid fa-arrow-up-right-from-square ms-auto text-muted small"></i>
                    </a>

                    <router-link
                      v-else
                      class="dropdown-item d-flex align-items-center gap-2"
                      :to="normalizeLink(p.lien)"
                    >
                      <img v-if="p.logo_url" :src="p.logo_url" class="zs-dd-logo" alt="" />
                      <i v-else class="fa-solid fa-sliders text-muted"></i>
                      <span>{{ p.nom }}</span>
                    </router-link>
                  </li>
                </template>

                <li><hr class="dropdown-divider" /></li>

                <li>
                  <h6 class="dropdown-header">Livraison</h6>
                </li>

                <li>
                  <router-link class="dropdown-item" to="/parametres/livraison/lieux">
                    <i class="fa-solid fa-location-dot me-2"></i>
                    Lieux de livraison
                  </router-link>
                </li>

                <li>
                  <router-link class="dropdown-item" to="/parametres/livraison/frais">
                    <i class="fa-solid fa-money-bill-wave me-2"></i>
                    Frais de livraison
                  </router-link>
                </li>

                <li><hr class="dropdown-divider" /></li>

                <li>
                  <router-link class="dropdown-item" to="/configuration">
                    <i class="fa-solid fa-gear me-2"></i>
                    Panneau de configuration
                  </router-link>
                </li>

                <li><hr class="dropdown-divider" /></li>

                <li>
                  <button class="dropdown-item text-danger" type="button" @click="logout">
                    <i class="fa-solid fa-right-from-bracket me-2"></i>
                    Se déconnecter
                  </button>
                </li>

              </ul>
            </div>
          </template>

        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.zs-menu-icon { font-size: 1.2rem; }

.zs-brand-click { cursor: pointer; }

.zs-dd-logo {
  width: 18px;
  height: 18px;
  border-radius: 6px;
  object-fit: cover;
}

@media (min-width: 992px) {
  .zs-nav-center { margin-left: auto; margin-right: auto; }

  .zs-icon-link {
    padding: .6rem .75rem;
    border-radius: .75rem;
    color: #6c757d;
    transition: background .15s ease, color .15s ease, transform .05s ease;
  }

  .zs-icon-link:hover {
    background: rgba(13,110,253,.08);
    color: #0d6efd;
  }

  .zs-icon-link.active {
    background: rgba(13,110,253,.18);
    color: #0d6efd;
    font-weight: 600;
  }

  .zs-icon-link.active .zs-menu-icon {
    transform: translateY(-1px);
  }
}
</style>
