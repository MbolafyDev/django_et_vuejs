<!-- src/views/auth/ProfileView.vue -->
<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref, nextTick } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore, type UserSexe } from "@/stores/auth";
import AppNavbar from "@/components/AppNavbar.vue";
import Modal from "bootstrap/js/dist/modal";

const auth = useAuthStore();
const router = useRouter();

const saving = ref(false);
const ok = ref("");
const err = ref("");

/* =========================
   ✅ Données formulaire (édition)
========================= */
const form = ref({
  first_name: "",
  last_name: "",
  adresse: "",
  numero_telephone: "",
  sexe: "" as UserSexe,
});

const photoProfilFile = ref<File | null>(null);
const photoCoverFile = ref<File | null>(null);

const previewProfil = ref<string | null>(null);
const previewCover = ref<string | null>(null);

const currentProfilUrl = computed(() => auth.user?.photo_profil_url || null);
const currentCoverUrl = computed(() => auth.user?.photo_couverture_url || null);

const displayName = computed(() => {
  const u = auth.user;
  if (!u) return "—";
  const full = `${u.first_name || ""} ${u.last_name || ""}`.trim();
  return full || u.username || u.email || "Utilisateur";
});

function fillFromUser() {
  const u = auth.user;
  if (!u) return;
  form.value.first_name = u.first_name || "";
  form.value.last_name = u.last_name || "";
  form.value.adresse = u.adresse || "";
  form.value.numero_telephone = u.numero_telephone || "";
  form.value.sexe = (u.sexe || "") as UserSexe;
}

function onPickProfil(e: Event) {
  const f = (e.target as HTMLInputElement)?.files?.[0] || null;
  photoProfilFile.value = f;
  previewProfil.value = f ? URL.createObjectURL(f) : null;
}

function onPickCover(e: Event) {
  const f = (e.target as HTMLInputElement)?.files?.[0] || null;
  photoCoverFile.value = f;
  previewCover.value = f ? URL.createObjectURL(f) : null;
}

function clearProfil() {
  photoProfilFile.value = null;
  previewProfil.value = null;
}

function clearCover() {
  photoCoverFile.value = null;
  previewCover.value = null;
}

function resetTempFiles() {
  clearProfil();
  clearCover();
}

/* =========================
   ✅ Modal édition
========================= */
const editModalEl = ref<HTMLElement | null>(null);
let editModal: Modal | null = null;

function openEditModal() {
  ok.value = "";
  err.value = "";
  fillFromUser();
  resetTempFiles();
  editModal?.show();
}

function closeEditModal() {
  editModal?.hide();
}

async function submit() {
  ok.value = "";
  err.value = "";

  if (!auth.isAuthenticated) {
    router.push({ name: "login" });
    return;
  }

  saving.value = true;
  try {
    await auth.updateProfile({
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      adresse: form.value.adresse,
      numero_telephone: form.value.numero_telephone,
      sexe: form.value.sexe,
      photo_profil: photoProfilFile.value,
      photo_couverture: photoCoverFile.value,
    });

    ok.value = "Profil mis à jour ✅";
    resetTempFiles();
    closeEditModal();
  } catch (e) {
    err.value = auth.lastError || "Erreur lors de la mise à jour du profil.";
  } finally {
    saving.value = false;
  }
}

function onHiddenModal() {
  // évite de garder des ObjectURL en mémoire
  resetTempFiles();
}

onMounted(async () => {
  // Auth
  if (!auth.isAuthenticated) {
    try {
      await auth.fetchMe();
    } catch (_) {}
  }
  if (!auth.isAuthenticated) {
    router.push({ name: "login" });
    return;
  }

  // Modal init
  await nextTick();
  if (editModalEl.value) {
    editModal = new Modal(editModalEl.value, { backdrop: "static", keyboard: false });
    editModalEl.value.addEventListener("hidden.bs.modal", onHiddenModal);
  }

  fillFromUser();
});

onBeforeUnmount(() => {
  if (editModalEl.value) {
    editModalEl.value.removeEventListener("hidden.bs.modal", onHiddenModal);
  }
  editModal?.hide();
  editModal = null;
});
</script>

<template>
  <div class="zs-root">
    <!-- ✅ NAVBAR (design = ton AppNavbar) -->
    <AppNavbar />

    <div class="container-fluid py-4 zs-page">
      <!-- ✅ Hero header (même esprit “glass/neo”) -->
      <div class="zs-hero mb-3">
        <div class="d-flex align-items-start justify-content-between flex-wrap gap-2">
          <div class="min-width-0">
            <div class="d-flex align-items-center gap-2 flex-wrap">
              <div class="zs-dot"></div>
              <h4 class="mb-0 zs-title">Mon profil</h4>
              <span class="zs-pill-soft">
                <i class="fa-solid fa-user-shield me-1"></i> Compte
              </span>
            </div>
            <div class="text-muted small mt-1">
              Consultez vos informations et modifiez-les dans une fenêtre modale
            </div>
          </div>

          <div class="d-flex gap-2 flex-wrap">
            <button class="btn btn-primary zs-btn" type="button" @click="openEditModal" :disabled="saving">
              <i class="fa-solid fa-pen-to-square me-2"></i> Modifier
            </button>
            <button class="btn btn-outline-secondary zs-btn" type="button" @click="router.back()" :disabled="saving">
              <i class="fa-solid fa-arrow-left me-2"></i> Retour
            </button>
          </div>
        </div>
      </div>

      <div v-if="err" class="alert alert-danger py-2 mb-3">{{ err }}</div>
      <div v-if="ok" class="alert alert-success py-2 mb-3">{{ ok }}</div>

      <div class="row g-3">
        <!-- ✅ Carte “profil” -->
        <div class="col-12 col-lg-5">
          <div class="card shadow-sm zs-card">
            <div class="card-body p-0">
              <!-- Cover -->
              <div class="zs-cover">
                <img v-if="currentCoverUrl" :src="currentCoverUrl" alt="Couverture" />
                <div v-else class="zs-cover-empty">
                  <i class="fa-regular fa-image"></i>
                  <div class="small mt-1">Aucune couverture</div>
                </div>
              </div>

              <!-- Avatar + infos rapides -->
              <div class="p-3">
                <div class="d-flex align-items-center gap-3">
                  <div class="zs-avatar">
                    <img v-if="currentProfilUrl" :src="currentProfilUrl" alt="Profil" />
                    <div v-else class="zs-avatar-empty">
                      <i class="fa-solid fa-user"></i>
                    </div>
                  </div>

                  <div class="min-width-0">
                    <div class="fw-bold zs-name zs-ellipsis">{{ displayName }}</div>
                    <div class="text-muted small zs-ellipsis">
                      <i class="fa-solid fa-badge-check me-1"></i> Rôle :
                      <b>{{ auth.user?.role || "—" }}</b>
                    </div>
                    <div class="text-muted small zs-ellipsis" v-if="auth.user?.email">
                      <i class="fa-solid fa-envelope me-1"></i> {{ auth.user.email }}
                    </div>
                  </div>
                </div>

                <hr class="my-3" />

                <div class="zs-kv">
                  <div class="zs-kv-row">
                    <div class="zs-kv-k">Adresse</div>
                    <div class="zs-kv-v">{{ auth.user?.adresse || "—" }}</div>
                  </div>

                  <div class="zs-kv-row">
                    <div class="zs-kv-k">Téléphone</div>
                    <div class="zs-kv-v">{{ auth.user?.numero_telephone || "—" }}</div>
                  </div>

                  <div class="zs-kv-row">
                    <div class="zs-kv-k">Sexe</div>
                    <div class="zs-kv-v">{{ auth.user?.sexe || "—" }}</div>
                  </div>
                </div>

                <div class="zs-tip mt-3">
                  <i class="fa-solid fa-circle-info me-2"></i>
                  Pour modifier vos infos et vos photos, cliquez sur <b>Modifier</b>.
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ✅ Carte “sécurité / infos” -->
        <div class="col-12 col-lg-7">
          <div class="card shadow-sm zs-card">
            <div class="card-body">
              <div class="d-flex align-items-center justify-content-between flex-wrap gap-2">
                <div class="fw-bold">
                  <i class="fa-solid fa-id-card me-2 text-primary"></i>
                  Informations du compte
                </div>
                <button class="btn btn-outline-secondary btn-sm zs-btn" type="button" @click="openEditModal">
                  <i class="fa-solid fa-pen me-2"></i> Modifier via modal
                </button>
              </div>

              <div class="row g-2 mt-2">
                <div class="col-12 col-md-6">
                  <div class="zs-field">
                    <div class="zs-field-label">Prénom</div>
                    <div class="zs-field-val">{{ auth.user?.first_name || "—" }}</div>
                  </div>
                </div>
                <div class="col-12 col-md-6">
                  <div class="zs-field">
                    <div class="zs-field-label">Nom</div>
                    <div class="zs-field-val">{{ auth.user?.last_name || "—" }}</div>
                  </div>
                </div>

                <div class="col-12">
                  <div class="zs-field">
                    <div class="zs-field-label">Adresse</div>
                    <div class="zs-field-val">{{ auth.user?.adresse || "—" }}</div>
                  </div>
                </div>

                <div class="col-12 col-md-6">
                  <div class="zs-field">
                    <div class="zs-field-label">Téléphone</div>
                    <div class="zs-field-val">{{ auth.user?.numero_telephone || "—" }}</div>
                  </div>
                </div>

                <div class="col-12 col-md-6">
                  <div class="zs-field">
                    <div class="zs-field-label">Sexe</div>
                    <div class="zs-field-val">{{ auth.user?.sexe || "—" }}</div>
                  </div>
                </div>
              </div>

              <div class="alert alert-info mt-3 small mb-0">
                <i class="fa-solid fa-circle-info me-2"></i>
                Le rôle (<b>{{ auth.user?.role || "—" }}</b>) est défini par l’administrateur.
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ✅ MODAL: Édition profil -->
      <div class="modal fade" tabindex="-1" ref="editModalEl" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
          <div class="modal-content zs-modal">
            <div class="modal-header">
              <div class="d-flex align-items-center gap-2">
                <div class="zs-modal-ico"><i class="fa-solid fa-user-pen"></i></div>
                <div>
                  <div class="fw-bold">Modifier mon profil</div>
                  <div class="text-muted small">Infos + photos (profil & couverture)</div>
                </div>
              </div>
              <button type="button" class="btn-close" aria-label="Close" @click="closeEditModal"></button>
            </div>

            <form @submit.prevent="submit">
              <div class="modal-body">
                <div v-if="err" class="alert alert-danger py-2 mb-3">{{ err }}</div>

                <div class="row g-3">
                  <!-- Photos -->
                  <div class="col-12 col-lg-5">
                    <div class="zs-panel">
                      <div class="fw-bold mb-2">
                        <i class="fa-solid fa-image me-2 text-primary"></i> Photos
                      </div>

                      <!-- Couverture -->
                      <div class="mb-3">
                        <label class="form-label fw-semibold">Photo de couverture</label>

                        <div class="zs-cover zs-cover--mini">
                          <img
                            v-if="previewCover || currentCoverUrl"
                            :src="previewCover || currentCoverUrl"
                            alt="Couverture"
                          />
                          <div v-else class="zs-cover-empty">
                            <i class="fa-regular fa-image"></i>
                            <div class="small mt-1">Aucune couverture</div>
                          </div>
                        </div>

                        <div class="d-flex gap-2 mt-2 flex-wrap">
                          <label class="btn btn-outline-primary btn-sm zs-btn">
                            <i class="fa-solid fa-upload me-2"></i> Choisir
                            <input type="file" class="d-none" accept="image/*" @change="onPickCover" />
                          </label>

                          <button
                            class="btn btn-outline-secondary btn-sm zs-btn"
                            type="button"
                            @click="clearCover"
                            :disabled="saving"
                          >
                            <i class="fa-solid fa-xmark me-2"></i> Retirer
                          </button>
                        </div>
                        <div class="text-muted small mt-1">Recommandé: 1200×400</div>
                      </div>

                      <!-- Profil -->
                      <div>
                        <label class="form-label fw-semibold">Photo de profil</label>

                        <div class="zs-avatar-row">
                          <div class="zs-avatar zs-avatar--mini">
                            <img v-if="previewProfil || currentProfilUrl" :src="previewProfil || currentProfilUrl" alt="Profil" />
                            <div v-else class="zs-avatar-empty">
                              <i class="fa-solid fa-user"></i>
                            </div>
                          </div>

                          <div class="flex-grow-1">
                            <div class="d-flex gap-2 flex-wrap">
                              <label class="btn btn-outline-primary btn-sm zs-btn">
                                <i class="fa-solid fa-upload me-2"></i> Choisir
                                <input type="file" class="d-none" accept="image/*" @change="onPickProfil" />
                              </label>

                              <button
                                class="btn btn-outline-secondary btn-sm zs-btn"
                                type="button"
                                @click="clearProfil"
                                :disabled="saving"
                              >
                                <i class="fa-solid fa-xmark me-2"></i> Retirer
                              </button>
                            </div>
                            <div class="text-muted small mt-1">Recommandé: 400×400</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Infos -->
                  <div class="col-12 col-lg-7">
                    <div class="zs-panel">
                      <div class="fw-bold mb-2">
                        <i class="fa-solid fa-id-card me-2 text-primary"></i> Informations
                      </div>

                      <div class="row g-2">
                        <div class="col-12 col-md-6">
                          <label class="form-label">Prénom</label>
                          <input v-model="form.first_name" type="text" class="form-control" :disabled="saving" />
                        </div>

                        <div class="col-12 col-md-6">
                          <label class="form-label">Nom</label>
                          <input v-model="form.last_name" type="text" class="form-control" :disabled="saving" />
                        </div>

                        <div class="col-12">
                          <label class="form-label">Adresse</label>
                          <input v-model="form.adresse" type="text" class="form-control" :disabled="saving" />
                        </div>

                        <div class="col-12 col-md-6">
                          <label class="form-label">Téléphone</label>
                          <input
                            v-model="form.numero_telephone"
                            type="tel"
                            class="form-control"
                            placeholder="+261 34 00 000 00"
                            :disabled="saving"
                          />
                        </div>

                        <div class="col-12 col-md-6">
                          <label class="form-label">Sexe</label>
                          <select v-model="form.sexe" class="form-select" :disabled="saving">
                            <option value="">—</option>
                            <option value="M">Masculin</option>
                            <option value="F">Féminin</option>
                            <option value="AUTRE">Autre</option>
                          </select>
                        </div>
                      </div>

                      <button
                        class="btn btn-outline-secondary btn-sm zs-btn mt-3"
                        type="button"
                        @click="fillFromUser"
                        :disabled="saving"
                      >
                        <i class="fa-solid fa-rotate me-2"></i> Réinitialiser depuis mon compte
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="modal-footer">
                <button class="btn btn-outline-secondary zs-btn" type="button" @click="closeEditModal" :disabled="saving">
                  <i class="fa-solid fa-xmark me-2"></i> Annuler
                </button>

                <button class="btn btn-primary zs-btn" type="submit" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="fa-solid fa-floppy-disk me-2"></i>
                  Enregistrer
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
      <!-- /MODAL -->
    </div>
  </div>
</template>

<style scoped>
.min-width-0 { min-width: 0; }
.zs-ellipsis { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ✅ Page fond “tech” comme tes pages */
.zs-page{
  background:
    radial-gradient(900px 360px at 10% 0%, rgba(13,110,253,.10), transparent 55%),
    radial-gradient(800px 320px at 90% 10%, rgba(25,135,84,.08), transparent 55%),
    transparent;
}

/* ✅ Hero */
.zs-hero{
  border-radius: 18px;
  border: 1px solid rgba(0,0,0,.08);
  background: rgba(255,255,255,.72);
  backdrop-filter: blur(12px);
  box-shadow: 0 14px 34px rgba(0,0,0,.10);
  padding: 14px 14px;
}
.zs-dot{
  width: 10px; height: 10px; border-radius: 999px;
  background: rgba(13,110,253,1);
  box-shadow: 0 0 0 5px rgba(13,110,253,.14);
}
.zs-title{
  font-weight: 950;
  letter-spacing: .2px;
  color: #0f172a;
}
.zs-pill-soft{
  font-size: .78rem;
  font-weight: 900;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,.06);
  background: rgba(255,255,255,.65);
  color: rgba(15,23,42,.70);
}

.zs-btn{ border-radius: 14px; font-weight: 800; }

/* ✅ Cards */
.zs-card{
  border-radius: 18px;
  border: 1px solid rgba(0,0,0,.08);
  background: rgba(255,255,255,.72);
  backdrop-filter: blur(12px);
}

/* ✅ Cover + avatar */
.zs-cover{
  width: 100%;
  height: 190px;
  overflow: hidden;
  border-bottom: 1px solid rgba(0,0,0,.06);
  background: rgba(255,255,255,.60);
  display:flex;
  align-items:center;
  justify-content:center;
}
.zs-cover img{ width: 100%; height: 100%; object-fit: cover; }
.zs-cover-empty{ text-align:center; color: rgba(15,23,42,.55); }
.zs-cover-empty i{ font-size: 1.4rem; }

.zs-cover--mini{
  height: 150px;
  border-radius: 14px;
  border: 1px solid rgba(0,0,0,.10);
  border-bottom: 1px solid rgba(0,0,0,.10);
}

.zs-avatar{
  width: 92px;
  height: 92px;
  border-radius: 26px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.70);
  display:flex;
  align-items:center;
  justify-content:center;
  flex: 0 0 auto;
  box-shadow: 0 12px 22px rgba(0,0,0,.08);
}
.zs-avatar img{ width: 100%; height: 100%; object-fit: cover; }
.zs-avatar-empty{ color: rgba(15,23,42,.55); font-size: 1.4rem; }

.zs-avatar--mini{
  width: 78px;
  height: 78px;
  border-radius: 22px;
  box-shadow: none;
}

.zs-avatar-row{ display:flex; gap: 12px; align-items:center; }

/* ✅ KV bloc */
.zs-kv{ display:flex; flex-direction:column; gap: 10px; }
.zs-kv-row{
  display:flex; align-items:flex-start; justify-content:space-between; gap: 12px;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(0,0,0,.06);
  background: rgba(255,255,255,.60);
}
.zs-kv-k{ font-size: .78rem; font-weight: 900; color: rgba(15,23,42,.65); }
.zs-kv-v{ font-weight: 850; color: rgba(15,23,42,.86); text-align:right; }

.zs-name{ font-size: 1.05rem; font-weight: 950; color: #0f172a; }

.zs-tip{
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(13,110,253,.18);
  background: rgba(13,110,253,.06);
  color: rgba(15,23,42,.80);
  font-weight: 700;
}

/* ✅ “Field” look */
.zs-field{
  padding: 12px 12px;
  border-radius: 14px;
  border: 1px solid rgba(0,0,0,.06);
  background: rgba(255,255,255,.60);
}
.zs-field-label{ font-size: .78rem; font-weight: 900; color: rgba(15,23,42,.62); }
.zs-field-val{ font-weight: 900; color: rgba(15,23,42,.86); margin-top: 2px; }

/* ✅ Modal (glass) */
.zs-modal{
  border-radius: 18px;
  border: 1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.92);
  backdrop-filter: blur(12px);
  box-shadow: 0 24px 60px rgba(0,0,0,.18);
  overflow: hidden;
}
.zs-modal-ico{
  width: 40px; height: 40px;
  border-radius: 14px;
  display:flex; align-items:center; justify-content:center;
  border: 1px solid rgba(13,110,253,.18);
  background: rgba(13,110,253,.08);
  color: rgba(13,110,253,1);
}
.zs-panel{
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,.08);
  background: rgba(255,255,255,.72);
  padding: 12px;
}
</style>
