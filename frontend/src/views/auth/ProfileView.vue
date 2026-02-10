<!-- src/views/auth/ProfileView.vue -->
<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore, type UserSexe } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();

const saving = ref(false);
const ok = ref("");
const err = ref("");

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
    clearProfil();
    clearCover();
  } catch (e) {
    err.value = auth.lastError || "Erreur lors de la mise à jour du profil.";
  } finally {
    saving.value = false;
  }
}

onMounted(async () => {
  if (!auth.isAuthenticated) {
    // si tokens en storage, initFromStorage() peut déjà être appelé ailleurs,
    // mais on sécurise :
    try {
      await auth.fetchMe();
    } catch (_) {}
  }
  if (!auth.isAuthenticated) {
    router.push({ name: "login" });
    return;
  }
  fillFromUser();
});
</script>

<template>
  <div class="container py-4">
    <div class="d-flex align-items-start justify-content-between flex-wrap gap-2 mb-3">
      <div class="min-width-0">
        <h4 class="mb-0 fw-bold">Mon profil</h4>
        <div class="text-muted small">Mettre à jour vos informations et vos photos</div>
      </div>

      <button class="btn btn-outline-secondary" type="button" @click="fillFromUser" :disabled="saving">
        <i class="fa-solid fa-rotate me-2"></i> Réinitialiser
      </button>
    </div>

    <div v-if="err" class="alert alert-danger py-2">{{ err }}</div>
    <div v-if="ok" class="alert alert-success py-2">{{ ok }}</div>

    <div class="row g-3">
      <!-- Photos -->
      <div class="col-12 col-lg-5">
        <div class="card shadow-sm zs-card">
          <div class="card-body">
            <div class="fw-bold mb-2">
              <i class="fa-solid fa-image me-2 text-primary"></i> Photos
            </div>

            <!-- Couverture -->
            <div class="mb-3">
              <label class="form-label fw-semibold">Photo de couverture</label>

              <div class="zs-cover">
                <img
                  v-if="previewCover || currentCoverUrl"
                  :src="previewCover || currentCoverUrl"
                  alt="Couverture"
                />
                <div v-else class="zs-placeholder">
                  <i class="fa-regular fa-image"></i>
                  <div class="small">Aucune couverture</div>
                </div>
              </div>

              <div class="d-flex gap-2 mt-2 flex-wrap">
                <label class="btn btn-outline-primary btn-sm">
                  <i class="fa-solid fa-upload me-2"></i> Choisir
                  <input type="file" class="d-none" accept="image/*" @change="onPickCover" />
                </label>

                <button class="btn btn-outline-secondary btn-sm" type="button" @click="clearCover" :disabled="saving">
                  <i class="fa-solid fa-xmark me-2"></i> Retirer
                </button>
              </div>
              <div class="text-muted small mt-1">Formats: JPG/PNG/WebP. Taille recommandée: 1200×400</div>
            </div>

            <!-- Profil -->
            <div>
              <label class="form-label fw-semibold">Photo de profil</label>

              <div class="zs-avatar-row">
                <div class="zs-avatar">
                  <img
                    v-if="previewProfil || currentProfilUrl"
                    :src="previewProfil || currentProfilUrl"
                    alt="Profil"
                  />
                  <div v-else class="zs-avatar-placeholder">
                    <i class="fa-solid fa-user"></i>
                  </div>
                </div>

                <div class="flex-grow-1">
                  <div class="d-flex gap-2 flex-wrap">
                    <label class="btn btn-outline-primary btn-sm">
                      <i class="fa-solid fa-upload me-2"></i> Choisir
                      <input type="file" class="d-none" accept="image/*" @change="onPickProfil" />
                    </label>

                    <button class="btn btn-outline-secondary btn-sm" type="button" @click="clearProfil" :disabled="saving">
                      <i class="fa-solid fa-xmark me-2"></i> Retirer
                    </button>
                  </div>
                  <div class="text-muted small mt-1">Formats: JPG/PNG/WebP. Taille recommandée: 400×400</div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>

      <!-- Infos -->
      <div class="col-12 col-lg-7">
        <div class="card shadow-sm zs-card">
          <div class="card-body">
            <div class="fw-bold mb-2">
              <i class="fa-solid fa-id-card me-2 text-primary"></i> Informations
            </div>

            <form @submit.prevent="submit">
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

              <div class="d-flex gap-2 mt-3 flex-wrap">
                <button class="btn btn-primary" type="submit" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="fa-solid fa-floppy-disk me-2"></i>
                  Enregistrer
                </button>

                <button class="btn btn-outline-secondary" type="button" @click="router.back()" :disabled="saving">
                  <i class="fa-solid fa-arrow-left me-2"></i> Retour
                </button>
              </div>
            </form>

          </div>
        </div>

        <div class="alert alert-info mt-3 small mb-0">
          <i class="fa-solid fa-circle-info me-2"></i>
          Le rôle (<b>{{ auth.user?.role || "—" }}</b>) est défini par l’administrateur.
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.min-width-0{ min-width:0; }

.zs-card{
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,.08);
}

.zs-cover{
  width: 100%;
  height: 160px;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.7);
  display:flex;
  align-items:center;
  justify-content:center;
}
.zs-cover img{
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.zs-placeholder{
  color: rgba(15,23,42,.55);
  text-align:center;
}
.zs-placeholder i{ font-size: 1.4rem; margin-bottom: 6px; }

.zs-avatar-row{
  display:flex;
  gap: 12px;
  align-items:center;
}
.zs-avatar{
  width: 78px;
  height: 78px;
  border-radius: 22px;
  overflow:hidden;
  border: 1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.7);
  display:flex;
  align-items:center;
  justify-content:center;
  flex: 0 0 auto;
}
.zs-avatar img{
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.zs-avatar-placeholder{
  color: rgba(15,23,42,.55);
  font-size: 1.2rem;
}
</style>
