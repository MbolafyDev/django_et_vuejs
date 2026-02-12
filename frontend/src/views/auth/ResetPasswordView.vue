<!-- frontend/src/views/auth/ResetPasswordView.vue -->
<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const new_password = ref("");
const error = ref<string | null>(null);
const showPassword = ref(false);

const canSubmit = computed(() => !!new_password.value && !auth.loading);

const submit = async () => {
  error.value = null;

  try {
    const uid = typeof route.query.uid === "string" ? route.query.uid : "";
    const token = typeof route.query.token === "string" ? route.query.token : "";

    if (!uid || !token) {
      error.value = "Lien invalide ou incomplet.";
      return;
    }

    await auth.resetPassword(uid, token, new_password.value);
    router.push("/login");
  } catch (e) {
    error.value = "Lien invalide ou expiré";
  }
};
</script>

<template>
  <div class="zs-dashboard zs-auth">
    <div class="container py-4">
      <div class="row justify-content-center">
        <div class="col-12 col-md-10 col-lg-7 col-xl-6">
          <div class="zs-card">
            <!-- Title -->
            <div class="text-center mb-3">
              <h3 class="mb-1 zs-title">Nouveau mot de passe</h3>
              <div class="text-muted small">
                Définissez un nouveau mot de passe pour votre compte
              </div>
            </div>

            <div v-if="error" class="alert alert-danger py-2">
              <i class="fa-solid fa-triangle-exclamation me-1"></i>
              {{ error }}
            </div>

            <div class="d-flex align-items-center justify-content-between mb-2">
              <div class="fw-semibold">Réinitialisation</div>
              <div class="text-muted small">
                <i class="fa-solid fa-lock me-1"></i> Nouveau mot de passe
              </div>
            </div>

            <form @submit.prevent="submit" class="row g-3">
              <div class="col-12">
                <label class="form-label small mb-1">Nouveau mot de passe</label>

                <div class="input-group input-group-sm">
                  <span class="input-group-text bg-white">
                    <i class="fa-solid fa-lock"></i>
                  </span>

                  <input
                    v-model="new_password"
                    :type="showPassword ? 'text' : 'password'"
                    class="form-control"
                    placeholder="••••••••"
                    autocomplete="new-password"
                    :disabled="auth.loading"
                    required
                  />

                  <button
                    class="btn btn-outline-secondary"
                    type="button"
                    :disabled="auth.loading"
                    @click="showPassword = !showPassword"
                    :title="showPassword ? 'Masquer' : 'Afficher'"
                  >
                    <i :class="showPassword ? 'fa-regular fa-eye-slash' : 'fa-regular fa-eye'"></i>
                  </button>
                </div>

                
              </div>

              <div class="col-12 d-flex align-items-center justify-content-between flex-wrap gap-2">
                <div class="text-muted small mt-2">
                  <i class="fa-solid fa-circle-info me-1"></i>
                  Choisissez un mot de passe fort (au moins 6 caractères).
                </div>

                <button class="btn btn-sm btn-primary" type="submit" :disabled="!canSubmit">
                  <span v-if="auth.loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="fa-solid fa-rotate me-2"></i>
                  Réinitialiser
                </button>
              </div>

              <div class="col-12 d-flex justify-content-center align-items-center flex-wrap gap-2">
                <div class="text-muted small">
                  Retour ?
                  <router-link to="/login" class="text-decoration-none fw-semibold">
                    Se connecter
                  </router-link>
                </div>
              </div>
            </form>

            <div v-if="auth.loading" class="text-muted small mt-3 text-center">
              Chargement...
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ✅ Même base que tes pages */
.zs-dashboard {
  background: #f8fafc;
  min-height: 100vh;
}

.zs-title {
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #0f172a;
}

/* ✅ Card style identique */
.zs-card {
  background: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 14px;
  padding: 18px;
  box-shadow: 0 10px 28px rgba(2, 6, 23, 0.06);
}

/* ✅ mêmes détails inputs que login/register/forgot */
.input-group-text {
  border-right: 0;
}
.input-group .form-control {
  border-left: 0;
}
</style>
