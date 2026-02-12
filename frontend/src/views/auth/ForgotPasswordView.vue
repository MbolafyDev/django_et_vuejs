<!-- frontend/src/views/auth/ForgotPasswordView.vue -->
<script setup lang="ts">
import { computed, ref } from "vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();

const email = ref("");
const message = ref<string | null>(null);
const error = ref<string | null>(null);
const devLink = ref<string | null>(null);

const canSubmit = computed(() => !!email.value.trim() && !auth.loading);

const submit = async () => {
  message.value = null;
  error.value = null;
  devLink.value = null;

  try {
    const res = await auth.forgotPassword(email.value.trim());
    message.value = res?.data?.message || "Si l'email existe, un lien a été envoyé.";
    devLink.value = res?.data?.reset_link_dev || null;
  } catch (e) {
    error.value = "Une erreur est survenue. Veuillez réessayer.";
  }
};
</script>

<template>
  <div class="zs-dashboard zs-auth">
    <div class="container py-4">
      <div class="row justify-content-center">
        <div class="col-12 col-md-10 col-lg-7 col-xl-6">
          <div class="zs-card">
            <div class="text-center mb-3">
              <h3 class="mb-1 zs-title">Mot de passe oublié</h3>
              <div class="text-muted small">Entrez votre email pour recevoir un lien</div>
            </div>

            <div v-if="error" class="alert alert-danger py-2">
              <i class="fa-solid fa-triangle-exclamation me-1"></i>
              {{ error }}
            </div>

            <div v-if="message" class="alert alert-success py-2">
              <i class="fa-solid fa-circle-check me-1"></i>
              {{ message }}
            </div>

            <!-- ✅ DEV LINK visible -->
            <div v-if="devLink" class="alert alert-info py-2">
              <div class="fw-semibold mb-1">Lien DEV :</div>
              <a :href="devLink" class="text-decoration-none" target="_blank" rel="noreferrer">
                {{ devLink }}
              </a>
            </div>

            <form @submit.prevent="submit" class="row g-3">
              <div class="col-12">
                <label class="form-label small mb-1">Adresse email</label>
                <div class="input-group input-group-sm">
                  <span class="input-group-text bg-white">
                    <i class="fa-regular fa-envelope"></i>
                  </span>
                  <input
                    v-model="email"
                    type="email"
                    class="form-control"
                    placeholder="ex: nom@gmail.com"
                    autocomplete="email"
                    :disabled="auth.loading"
                    required
                  />
                </div>
              </div>

              <div class="col-12 d-flex align-items-center justify-content-between flex-wrap gap-2">
                <div class="text-muted small">
                  <i class="fa-solid fa-shield-halved me-1"></i>
                  Demande sécurisée
                </div>

                <button class="btn btn-sm btn-primary" type="submit" :disabled="!canSubmit">
                  <span v-if="auth.loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="fa-solid fa-paper-plane me-2"></i>
                  Envoyer le lien
                </button>
              </div>

              <div class="col-12 d-flex justify-content-between align-items-center flex-wrap gap-2">
                <div class="text-muted small">
                  Retour ?
                  <router-link to="/login" class="text-decoration-none fw-semibold">
                    Se connecter
                  </router-link>
                </div>

                <router-link to="/login" class="text-decoration-none fw-semibold small">
                  <i class="fa-solid fa-right-to-bracket me-1"></i>
                  Retour à la connexion
                </router-link>
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
.zs-dashboard {
  background: #f8fafc;
  min-height: 100vh;
}
.zs-title {
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #0f172a;
}
.zs-card {
  background: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 14px;
  padding: 18px;
  box-shadow: 0 10px 28px rgba(2, 6, 23, 0.06);
}
.input-group-text {
  border-right: 0;
}
.input-group .form-control {
  border-left: 0;
}
</style>
