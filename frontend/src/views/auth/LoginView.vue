<!-- frontend/src/views/auth/LoginView.vue -->
<script setup lang="ts">
import { computed, ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRouter, useRoute } from "vue-router";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const email = ref("");
const password = ref("");
const error = ref<string | null>(null);
const showPassword = ref(false);

const canSubmit = computed(() => !!email.value.trim() && !!password.value && !auth.loading);

const submit = async () => {
  error.value = null;

  try {
    const next = typeof route.query.next === "string" ? route.query.next : "";
    await auth.login(email.value.trim(), password.value, router, next || undefined);
  } catch (e) {
    error.value = auth.lastError || "Identifiants invalides ou erreur réseau.";
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
              <h3 class="mb-1 zs-title">Connexion</h3>
              <div class="text-muted small">Accédez à votre espace</div>
            </div>

            <div v-if="error" class="alert alert-danger py-2">
              <i class="fa-solid fa-triangle-exclamation me-1"></i>
              {{ error }}
            </div>

            <div class="d-flex align-items-center justify-content-between mb-2">
              <div class="fw-semibold">Identifiants</div>
              <div class="text-muted small">
                <i class="fa-regular fa-envelope me-1"></i> Email + mot de passe
              </div>
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

              <div class="col-12">
                <label class="form-label small mb-1">Mot de passe</label>
                <div class="input-group input-group-sm">
                  <span class="input-group-text bg-white">
                    <i class="fa-solid fa-lock"></i>
                  </span>
                  <input
                    v-model="password"
                    :type="showPassword ? 'text' : 'password'"
                    class="form-control"
                    placeholder="••••••••"
                    autocomplete="current-password"
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
                <div class="text-muted small">
                  <i class="fa-solid fa-shield-halved me-1"></i>
                  Session sécurisée
                </div>

                <button class="btn btn-sm btn-primary" type="submit" :disabled="!canSubmit">
                  <span v-if="auth.loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="fa-solid fa-right-to-bracket me-2"></i>
                  Se connecter
                </button>
              </div>

              <!-- ✅ Bloc modifié : Register + Forgot password ensemble -->
              <div class="col-12 d-flex justify-content-between align-items-center flex-wrap gap-2">
                <div class="text-muted small">
                  Besoin d’aide ?
                  <router-link to="/forgot-password" class="text-decoration-none fw-semibold">
                    Réinitialiser le mot de passe
                  </router-link>
                </div>

                <router-link to="/register" class="text-decoration-none fw-semibold small">
                  <i class="fa-solid fa-user-plus me-1"></i>
                  Créer un compte
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
