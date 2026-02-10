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

/* ===========================
   ✅ Role helpers
=========================== */
const isAdmin = computed(() => auth.user?.role === "ADMIN");

/* ===========================
   ✅ Menus (avec Charges ADMIN ONLY)
=========================== */
const menus = computed(() => {
  const base = [
    { to: "/commandes", label: "Commandes", icon: "fa-solid fa-receipt" },
    // { to: "/encaissement", label: "Encaissement", icon: "fa-solid fa-cash-register" },
    // { to: "/conflivraison", label: "Livraison", icon: "fa-solid fa-truck-fast" },
    // { to: "/achats", label: "Achat", icon: "fa-solid fa-cart-shopping" },
    { to: "/articles", label: "Articles", icon: "fa-solid fa-box" },
    { to: "/clients", label: "Clients", icon: "fa-solid fa-users" },
  ];

  // ✅ Charges visible uniquement ADMIN
  if (isAdmin.value) {
    // ✅ Facturation ADMIN ONLY
    base.splice(1, 0, { to: "/factures", label: "Facturation", icon: "fa-solid fa-file-invoice-dollar" });
    base.splice(3, 0, { to: "/encaissement", label: "Encaissement", icon: "fa-solid fa-cash-register" });
    base.splice(4, 0, { to: "/conflivraison", label: "Livraison", icon: "fa-solid fa-truck-fast" });

    base.splice(2, 0, { to: "/charges", label: "Charges", icon: "fa-solid fa-coins" }); // après Facturation
    base.splice(5, 0, { to: "/achats", label: "Achat", icon: "fa-solid fa-cart-shopping" }); // après Facturation
  }

  return base;
});

const isActive = (path: string) => route.path.startsWith(path);

/* ===========================
   ✅ Helpers user display
=========================== */
const displayFirstName = computed(() => {
  const u = auth.user;
  if (!u) return "";
  const first = (u.first_name || "").trim();
  return first || u.username || u.email || "Utilisateur";
});


const userAvatar = computed(() => {
  const url = auth.user?.photo_profil_url || "";
  return url && url.trim().length > 0 ? url : null;
});

const userRoleLabel = computed(() => {
  const r = auth.user?.role;
  if (r === "ADMIN") return "Admin";
  if (r === "COMMUNITY_MANAGER") return "Community manager";
  if (r === "COMMERCIALE") return "Commerciale";
  return "Utilisateur";
});

/* ===========================
   Tooltips Bootstrap (hover seulement) - desktop only
=========================== */
function disposeAllTooltips() {
  document.querySelectorAll('[data-zs-tooltip="1"]').forEach((el) => {
    const instance = Tooltip.getInstance(el as Element);
    if (instance) instance.dispose();
  });
}
function initTooltipsHover() {
  if (window.matchMedia("(max-width: 991.98px)").matches) return;
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
   ✅ Sidebar mobile (TELEPORT vers <body>)
=========================== */
const isMobile = ref(false);
const sidebarOpen = ref(false);
const lastActiveEl = ref<HTMLElement | null>(null);

function updateIsMobile() {
  isMobile.value = window.matchMedia("(max-width: 991.98px)").matches;
  if (!isMobile.value && sidebarOpen.value) closeSidebar();
}

function lockScroll() {
  document.documentElement.classList.add("zs-no-scroll");
  document.body.classList.add("zs-no-scroll");
}
function unlockScroll() {
  document.documentElement.classList.remove("zs-no-scroll");
  document.body.classList.remove("zs-no-scroll");
}

function openSidebar() {
  lastActiveEl.value = document.activeElement as HTMLElement | null;
  sidebarOpen.value = true;
  lockScroll();
  nextTick(() => {
    const btn = document.querySelector(".zs-sb-close") as HTMLButtonElement | null;
    btn?.focus();
  });
}
function closeSidebar() {
  sidebarOpen.value = false;
  unlockScroll();
  nextTick(() => lastActiveEl.value?.focus?.());
}
function toggleSidebar() {
  sidebarOpen.value ? closeSidebar() : openSidebar();
}

function onToggleMenuClick() {
  if (isMobile.value) toggleSidebar();
}

function goTo(path: string) {
  closeSidebar();
  router.push(path);
}

function openExternal(url: string) {
  closeSidebar();
  window.open(url, "_blank", "noopener");
}

const logout = async () => {
  await auth.logout();
  closeSidebar();
  router.push({ name: "login" });
};

function onEsc(e: KeyboardEvent) {
  if (e.key === "Escape" && sidebarOpen.value) closeSidebar();
}

/* ===========================
   lifecycle
=========================== */
onMounted(async () => {
  updateIsMobile();
  window.addEventListener("resize", updateIsMobile);
  window.addEventListener("keydown", onEsc);

  await nextTick();
  initTooltipsHover();
  await loadConfigLinks();
});

onBeforeUnmount(() => {
  disposeAllTooltips();
  window.removeEventListener("resize", updateIsMobile);
  window.removeEventListener("keydown", onEsc);
  closeSidebar();
});

watch(
  () => route.fullPath,
  async () => {
    if (sidebarOpen.value) closeSidebar();
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
  <!-- ✅ NAVBAR GLASS -->
  <header class="zs-nav-wrap">
    <nav class="navbar navbar-expand-lg zs-navbar">
      <div class="container-fluid zs-nav-inner">
        <!-- ✅ Brand -->
        <router-link
          class="zs-brand d-flex align-items-center gap-2"
          :to="{ name: 'dashboard-stats' }"
          aria-label="Retour au dashboard statistiques"
          @click="closeSidebar"
        >
          <span class="zs-brand-logo">
            <img src="/logo.jpg" alt="Logo" />
          </span>
          <div class="zs-brand-text">
            <div class="zs-brand-name">MBOLAFY</div>
          </div>
        </router-link>

        <!-- ✅ Burger (mobile) -->
        <button class="navbar-toggler zs-toggler" type="button" aria-label="Menu" @click="onToggleMenuClick">
          <span class="zs-toggler-icon"></span>
        </button>

        <!-- ✅ DESKTOP -->
        <div class="navbar-collapse d-none d-lg-flex">
          <ul class="navbar-nav zs-nav-capsule">
            <li v-for="m in menus" :key="m.to" class="nav-item">
              <router-link
                :to="m.to"
                class="nav-link zs-nav-item"
                data-zs-tooltip="1"
                data-bs-placement="bottom"
                :title="m.label"
                :class="{ active: isActive(m.to) }"
              >
                <span class="zs-nav-ico">
                  <i :class="m.icon" aria-hidden="true"></i>
                </span>
                <span class="zs-nav-label">{{ m.label }}</span>
              </router-link>
            </li>
          </ul>

          <div class="ms-lg-auto zs-nav-right d-flex align-items-center gap-2">
            <template v-if="!auth.isAuthenticated">
              <router-link class="btn btn-outline-primary zs-btn zs-btn-neo" to="/register">
                <i class="fa-solid fa-user-plus me-2"></i> Inscription
              </router-link>
              <router-link class="btn btn-primary zs-btn zs-btn-neo" to="/login">
                <i class="fa-solid fa-right-to-bracket me-2"></i> Connexion
              </router-link>
            </template>

            <template v-else>
              <!-- ✅ User chip desktop -->
              <div class="zs-user d-none d-lg-flex align-items-center gap-2">
                <span v-if="userAvatar" class="zs-user-avatar">
                  <img :src="userAvatar" alt="avatar" />
                </span>
                <span v-else class="zs-user-dot"></span>
                <div class="d-flex flex-column lh-1">
                  <span class="zs-user-name">{{ displayFirstName }}</span>
                </div>
              </div>

              <!-- ✅ Dropdown paramètres -->
              <div class="nav-item dropdown">
                <button
                  class="btn zs-btn zs-btn-neo zs-btn-gear dropdown-toggle"
                  type="button"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                  data-zs-tooltip="1"
                  data-bs-placement="bottom"
                  title="Paramètres"
                >
                  <i class="fa-solid fa-gear"></i>
                </button>

                <ul class="dropdown-menu dropdown-menu-end shadow zs-dd" style="min-width: 310px;">
                  <!-- ✅ Profil -->
                  <li>
                    <router-link class="dropdown-item d-flex align-items-center gap-2" to="/profil">
                      <span class="zs-dd-ico">
                        <img v-if="userAvatar" :src="userAvatar" class="zs-dd-avatar" alt="" />
                        <i v-else class="fa-solid fa-user-pen"></i>
                      </span>
                      <div class="min-width-0">
                        <div class="fw-bold zs-ellipsis">{{ displayFirstName }}</div>
                        <div class="small text-muted zs-ellipsis">Modifier mon profil</div>
                      </div>
                      <i class="fa-solid fa-chevron-right ms-auto text-muted small"></i>
                    </router-link>
                  </li>

                  <li><hr class="dropdown-divider" /></li>

                  <!-- ✅ Configuration dynamique -->
                  <li>
                    <h6 class="dropdown-header d-flex align-items-center justify-content-between">
                      <span>Configuration</span>
                      <span v-if="configLoading" class="text-muted small">...</span>
                    </h6>
                  </li>

                  <li v-if="configLinks.length === 0">
                    <span class="dropdown-item-text text-muted small">Aucune page de configuration.</span>
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
                        <span class="zs-ellipsis">{{ p.nom }}</span>
                        <i class="fa-solid fa-arrow-up-right-from-square ms-auto text-muted small"></i>
                      </a>

                      <router-link v-else class="dropdown-item d-flex align-items-center gap-2" :to="normalizeLink(p.lien)">
                        <img v-if="p.logo_url" :src="p.logo_url" class="zs-dd-logo" alt="" />
                        <i v-else class="fa-solid fa-sliders text-muted"></i>
                        <span class="zs-ellipsis">{{ p.nom }}</span>
                      </router-link>
                    </li>
                  </template>

                  <li><hr class="dropdown-divider" /></li>

                  <li><h6 class="dropdown-header">Livraison</h6></li>
                  <li>
                    <router-link class="dropdown-item" to="/parametres/livraison/lieux">
                      <i class="fa-solid fa-location-dot me-2"></i> Lieux de livraison
                    </router-link>
                  </li>
                  <li>
                    <router-link class="dropdown-item" to="/parametres/livraison/frais">
                      <i class="fa-solid fa-money-bill-wave me-2"></i> Frais de livraison
                    </router-link>
                  </li>

                  <li><hr class="dropdown-divider" /></li>

                  <li>
                    <router-link class="dropdown-item" to="/configuration">
                      <i class="fa-solid fa-gear me-2"></i> Panneau de configuration
                    </router-link>
                  </li>

                  <li><hr class="dropdown-divider" /></li>

                  <li>
                    <button class="dropdown-item text-danger" type="button" @click="logout">
                      <i class="fa-solid fa-right-from-bracket me-2"></i> Se déconnecter
                    </button>
                  </li>
                </ul>
              </div>
            </template>
          </div>
        </div>
      </div>
    </nav>
  </header>

  <!-- ✅ SIDEBAR MOBILE -->
  <teleport to="body">
    <transition name="zs-sb">
      <div v-if="sidebarOpen" class="zs-sb-backdrop" @click.self="closeSidebar">
        <aside class="zs-sb" role="dialog" aria-modal="true" aria-label="Menu">
          <!-- Header -->
          <div class="zs-sb-head">
            <div class="d-flex align-items-center gap-2 min-width-0">
              <span class="zs-brand-logo zs-brand-logo--sm">
                <img src="/logo.jpg" alt="Logo" />
              </span>
              <div class="min-width-0">
                <div class="zs-sb-title zs-ellipsis3">MBOLAFY</div>
              </div>
            </div>

            <button class="btn zs-btn zs-btn-neo zs-sb-close" type="button" @click="closeSidebar" aria-label="Fermer">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <!-- User -->
          <div class="zs-sb-user" v-if="auth.isAuthenticated">
            <span v-if="userAvatar" class="zs-user-avatar zs-user-avatar--sb">
              <img :src="userAvatar" alt="avatar" />
            </span>
            <span v-else class="zs-user-dot"></span>

            <div class="min-width-0">
              <div class="fw-bold zs-ellipsis3">{{ displayFirstName }}</div>
            </div>
          </div>

          <div class="zs-sb-body">
            <!-- Navigation -->
            <div class="zs-sb-section-title">
              <i class="fa-solid fa-bars me-2 text-primary"></i> Navigation
            </div>

            <button
              v-for="m in menus"
              :key="m.to"
              class="zs-sb-link"
              type="button"
              :class="{ active: isActive(m.to) }"
              @click="goTo(m.to)"
            >
              <span class="zs-sb-ico"><i :class="m.icon"></i></span>
              <span class="zs-sb-label">{{ m.label }}</span>
              <i class="fa-solid fa-chevron-right ms-auto text-muted small"></i>
            </button>

            <!-- Livraison -->
            <div class="zs-sb-section-title mt-3">
              <i class="fa-solid fa-truck-fast me-2 text-primary"></i> Livraison
            </div>

            <button class="zs-sb-link" type="button" @click="goTo('/parametres/livraison/lieux')">
              <span class="zs-sb-ico"><i class="fa-solid fa-location-dot"></i></span>
              <span class="zs-sb-label">Lieux de livraison</span>
              <i class="fa-solid fa-chevron-right ms-auto text-muted small"></i>
            </button>

            <button class="zs-sb-link" type="button" @click="goTo('/parametres/livraison/frais')">
              <span class="zs-sb-ico"><i class="fa-solid fa-money-bill-wave"></i></span>
              <span class="zs-sb-label">Frais de livraison</span>
              <i class="fa-solid fa-chevron-right ms-auto text-muted small"></i>
            </button>

            <!-- Compte -->
            <div class="zs-sb-section-title mt-3">
              <i class="fa-solid fa-gear me-2 text-primary"></i> Compte & paramètres
            </div>

            <template v-if="!auth.isAuthenticated">
              <button class="zs-sb-link" type="button" @click="goTo('/register')">
                <span class="zs-sb-ico"><i class="fa-solid fa-user-plus"></i></span>
                <span class="zs-sb-label">Inscription</span>
                <i class="fa-solid fa-chevron-right ms-auto text-muted small"></i>
              </button>

              <button class="zs-sb-link" type="button" @click="goTo('/login')">
                <span class="zs-sb-ico"><i class="fa-solid fa-right-to-bracket"></i></span>
                <span class="zs-sb-label">Connexion</span>
                <i class="fa-solid fa-chevron-right ms-auto text-muted small"></i>
              </button>
            </template>

            <template v-else>
              <button class="zs-sb-link" type="button" @click="goTo('/profil')">
                <span class="zs-sb-ico"><i class="fa-solid fa-user-pen"></i></span>
                <span class="zs-sb-label">Mon profil</span>
                <i class="fa-solid fa-chevron-right ms-auto text-muted small"></i>
              </button>

              <div class="zs-sb-minihead d-flex align-items-center justify-content-between">
                <div class="small text-muted fw-bold">Configuration</div>
                <div class="small text-muted" v-if="configLoading">...</div>
              </div>

              <div v-if="configLinks.length === 0" class="small text-muted px-2 pb-2">
                Aucune page de configuration.
              </div>

              <template v-else>
                <button
                  v-for="p in configLinks"
                  :key="p.id"
                  class="zs-sb-link"
                  type="button"
                  @click="
                    normalizeLink(p.lien).startsWith('http')
                      ? openExternal(normalizeLink(p.lien))
                      : goTo(normalizeLink(p.lien))
                  "
                >
                  <span class="zs-sb-ico">
                    <img v-if="p.logo_url" :src="p.logo_url" class="zs-dd-logo" alt="" />
                    <i v-else class="fa-solid fa-sliders"></i>
                  </span>
                  <span class="zs-sb-label zs-ellipsis3">{{ p.nom }}</span>
                  <i class="fa-solid fa-arrow-right ms-auto text-muted small"></i>
                </button>
              </template>

              <button class="zs-sb-link" type="button" @click="goTo('/configuration')">
                <span class="zs-sb-ico"><i class="fa-solid fa-gear"></i></span>
                <span class="zs-sb-label">Panneau de configuration</span>
                <i class="fa-solid fa-arrow-right ms-auto text-muted small"></i>
              </button>

              <button class="zs-sb-link zs-sb-link--danger" type="button" @click="logout">
                <span class="zs-sb-ico"><i class="fa-solid fa-right-from-bracket"></i></span>
                <span class="zs-sb-label">Se déconnecter</span>
              </button>
            </template>
          </div>

          <div class="zs-sb-foot">
            <div class="small text-muted">App • MBOLAFY</div>
          </div>
        </aside>
      </div>
    </transition>
  </teleport>
</template>

<style scoped>
/* (identique à ta version — inchangé) */
.zs-nav-wrap{
  position: sticky;
  top: 0;
  z-index: 1050;
  padding: 10px 12px;
  background:
    radial-gradient(800px 260px at 15% 0%, rgba(13,110,253,.14), transparent 55%),
    radial-gradient(700px 240px at 90% 20%, rgba(25,135,84,.10), transparent 55%),
    rgba(247,248,251,.70);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0,0,0,.06);
}

.zs-navbar{
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 18px;
  background: rgba(255,255,255,.72);
  box-shadow: 0 14px 34px rgba(0,0,0,.10);
  backdrop-filter: blur(12px);
}

.zs-nav-inner{ padding-left: 10px; padding-right: 10px; }

.zs-brand{ text-decoration: none; user-select: none; }
.zs-brand-logo{
  width: 40px; height: 40px; border-radius: 14px; overflow: hidden;
  border: 1px solid rgba(0,0,0,.08);
  background: rgba(255,255,255,.80);
  box-shadow: 0 10px 18px rgba(0,0,0,.06);
}
.zs-brand-logo img{ width: 100%; height: 100%; object-fit: cover; }

.zs-brand-logo--sm{
  width: 34px; height: 34px; border-radius: 12px;
  box-shadow: 0 10px 18px rgba(0,0,0,.05);
}

.zs-brand-text{ line-height: 1.05; }
.zs-brand-name{ font-weight: 950; letter-spacing: .3px; color: #0f172a; }
.zs-brand-sub{ font-size: .72rem; color: rgba(15,23,42,.55); font-weight: 700; }

.zs-toggler{
  border: 1px solid rgba(0,0,0,.10);
  border-radius: 14px;
  padding: 8px 10px;
  background: rgba(255,255,255,.8);
  box-shadow: 0 10px 18px rgba(0,0,0,.06);
}
.zs-toggler:focus{ box-shadow: 0 0 0 4px rgba(13,110,253,.18); }
.zs-toggler-icon{
  display:inline-block;
  width: 22px; height: 22px;
  background:
    linear-gradient(#0f172a,#0f172a) 0 5px/100% 2px no-repeat,
    linear-gradient(#0f172a,#0f172a) 0 10px/100% 2px no-repeat,
    linear-gradient(#0f172a,#0f172a) 0 15px/100% 2px no-repeat;
  opacity: .75;
}

.zs-nav-capsule{
  margin: 10px auto 0;
  padding: 6px;
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,.06);
  background: rgba(255,255,255,.65);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.65);
  gap: 4px;
}

.zs-nav-item{
  display:flex; align-items:center; gap: 8px;
  padding: 8px 10px;
  border-radius: 999px;
  color: rgba(15,23,42,.70);
  font-weight: 800;
  text-decoration: none;
  transition: background .15s ease, transform .05s ease, color .15s ease;
  white-space: nowrap;
}
.zs-nav-ico{
  width: 28px; height: 28px;
  border-radius: 10px;
  display:flex; align-items:center; justify-content:center;
  border: 1px solid rgba(0,0,0,.06);
  background: rgba(255,255,255,.80);
}
.zs-nav-ico i{ font-size: .95rem; }
.zs-nav-label{ font-size: .86rem; display: inline-block; }

.zs-nav-item:hover{ background: rgba(13,110,253,.08); color: rgba(13,110,253,1); }
.zs-nav-item.active{
  background: linear-gradient(180deg, rgba(13,110,253,.20), rgba(255,255,255,.72));
  border: 1px solid rgba(13,110,253,.18);
  color: rgba(13,110,253,1);
}
.zs-nav-item.active .zs-nav-ico{ border-color: rgba(13,110,253,.18); }
.zs-nav-item.active .zs-nav-ico i{ transform: translateY(-1px); }

.zs-nav-right{ padding-top: 10px; }

.zs-user{
  padding: 8px 10px;
  border-radius: 14px;
  border: 1px solid rgba(0,0,0,.06);
  background: rgba(255,255,255,.65);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.65);
}
.zs-user-dot{
  width: 8px; height: 8px; border-radius: 999px;
  background: rgba(25,135,84,1);
  box-shadow: 0 0 0 4px rgba(25,135,84,.14);
}
.zs-user-avatar{
  width: 28px;
  height: 28px;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.80);
  flex: 0 0 auto;
}
.zs-user-avatar img{ width:100%; height:100%; object-fit:cover; }

.zs-user-name{ font-weight: 950; color: rgba(15,23,42,.78); font-size: .86rem; }
.zs-user-sub{ font-size: .70rem; color: rgba(15,23,42,.55); font-weight: 800; margin-top: 2px; }

.zs-btn{ border-radius: 14px; }
.zs-btn-neo{ box-shadow: 0 10px 18px rgba(0,0,0,.06); }
.zs-btn-gear{
  border: 1px solid rgba(13,110,253,.22);
  background: rgba(255,255,255,.85);
  color: rgba(13,110,253,1);
}

.zs-dd{
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,.08);
  background: rgba(255,255,255,.92);
  overflow: hidden;
}
.zs-dd-logo{
  width: 18px; height: 18px;
  border-radius: 6px;
  object-fit: cover;
  border: 1px solid rgba(0,0,0,.08);
}
.zs-dd-ico{
  width: 34px;
  height: 34px;
  border-radius: 12px;
  display:flex;
  align-items:center;
  justify-content:center;
  border: 1px solid rgba(0,0,0,.08);
  background: rgba(255,255,255,.80);
  flex: 0 0 auto;
}
.zs-dd-avatar{
  width: 26px;
  height: 26px;
  border-radius: 10px;
  object-fit: cover;
  border: 1px solid rgba(0,0,0,.08);
}

.zs-ellipsis{ max-width: 210px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.min-width-0{ min-width:0; }
.zs-ellipsis3{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

@media (min-width: 992px){
  .zs-nav-capsule{ margin-top: 0; }
  .zs-nav-right{ padding-top: 0; }
}
</style>

<style>
/* (identique à ta version — inchangé) */
.zs-no-scroll{ overflow: hidden !important; }

.zs-sb-backdrop{
  position: fixed;
  inset: 0;
  background: rgba(15,23,42,.35);
  z-index: 9999;
  display:flex;
  align-items: stretch;
  justify-content:flex-start;
}

.zs-sb{
  width: 75vw;
  max-width: 420px;
  height: 100%;
  background: rgba(255,255,255,.88);
  backdrop-filter: blur(14px);
  border-right: 1px solid rgba(0,0,0,.08);
  box-shadow: 18px 0 40px rgba(0,0,0,.18);
  display:flex;
  flex-direction: column;
}

.zs-sb-head{
  padding: 14px 12px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 10px;
  border-bottom: 1px solid rgba(0,0,0,.06);
  background:
    radial-gradient(600px 200px at 10% 0%, rgba(13,110,253,.10), transparent 60%),
    rgba(255,255,255,.72);
}

.zs-sb-title{ font-weight: 950; letter-spacing: .3px; color: #0f172a; }
.zs-sb-sub{ font-size: .72rem; color: rgba(15,23,42,.55); font-weight: 700; }

.zs-sb-close{
  border: 1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.85);
  width: 42px;
  height: 42px;
  display:flex;
  align-items:center;
  justify-content:center;
  border-radius: 14px;
}

.zs-sb-user{
  padding: 12px 12px 10px;
  display:flex;
  align-items:center;
  gap: 10px;
  border-bottom: 1px solid rgba(0,0,0,.06);
}

.zs-user-avatar--sb{
  width: 34px;
  height: 34px;
  border-radius: 14px;
}

.zs-sb-body{
  padding: 12px;
  overflow:auto;
  flex: 1 1 auto;
}

.zs-sb-section-title{
  font-size: .78rem;
  font-weight: 900;
  color: rgba(15,23,42,.72);
  margin-bottom: 8px;
}

.zs-sb-minihead{ padding: 8px 4px 6px; }

.zs-sb-link{
  width: 100%;
  display:flex;
  align-items:center;
  gap: 10px;
  padding: 10px 10px;
  border-radius: 14px;
  border: 1px solid rgba(0,0,0,.06);
  background: rgba(255,255,255,.68);
  color: rgba(15,23,42,.84);
  font-weight: 800;
  margin-bottom: 8px;
  transition: transform .05s ease, background .15s ease, border-color .15s ease;
}
.zs-sb-link:hover{
  background: rgba(13,110,253,.08);
  border-color: rgba(13,110,253,.18);
}

.zs-sb-link.active{
  background: linear-gradient(180deg, rgba(13,110,253,.18), rgba(255,255,255,.72));
  border-color: rgba(13,110,253,.22);
  color: rgba(13,110,253,1);
}

.zs-sb-link--danger{
  color: rgba(185,28,28,1);
  background: rgba(239,68,68,.08);
  border-color: rgba(239,68,68,.18);
}

.zs-sb-ico{
  width: 34px;
  height: 34px;
  border-radius: 12px;
  display:flex;
  align-items:center;
  justify-content:center;
  border: 1px solid rgba(0,0,0,.06);
  background: rgba(255,255,255,.78);
  flex: 0 0 auto;
}
.zs-sb-ico i{ font-size: 1rem; }

.zs-sb-foot{
  padding: 10px 12px;
  border-top: 1px solid rgba(0,0,0,.06);
  background: rgba(255,255,255,.70);
}

.zs-sb-enter-active, .zs-sb-leave-active{ transition: opacity .18s ease; }
.zs-sb-enter-from, .zs-sb-leave-to{ opacity: 0; }
.zs-sb-enter-active .zs-sb, .zs-sb-leave-active .zs-sb{ transition: transform .18s ease; }
.zs-sb-enter-from .zs-sb{ transform: translateX(-14px); }
.zs-sb-leave-to .zs-sb{ transform: translateX(-14px); }
</style>
