<!-- frontend/src/views/LoginView.vue -->
<script setup>
import { ref } from "vue";
import { useAuthStore } from "../../stores/auth";
import { useRouter, useRoute } from "vue-router";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const email = ref("");
const password = ref("");
const error = ref("");

const submit = async () => {
  error.value = "";
  try {
    await auth.login(email.value, password.value);

    const next =
      typeof route.query.next === "string" && route.query.next
        ? route.query.next
        : "/dashboard";

    router.push(next);
  } catch (e) {
    error.value = auth.lastError || "Identifiants invalides ou erreur réseau.";
  }
};
</script>

<template>
  <div class="container min-vh-100 d-flex align-items-center justify-content-center">
    <div class="row w-100 justify-content-center">
      <div class="col-12 col-sm-10 col-md-6 col-lg-4">
        <div class="card shadow-sm">
          <div class="card-body">
            <h4 class="card-title text-center mb-3">Connexion</h4>

            <div v-if="error" class="alert alert-danger py-2">
              {{ error }}
            </div>

            <form @submit.prevent="submit">
              <div class="mb-3">
                <label class="form-label">Adresse email</label>
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

              <div class="mb-3">
                <label class="form-label">Mot de passe</label>
                <input
                  v-model="password"
                  type="password"
                  class="form-control"
                  placeholder="••••••••"
                  autocomplete="current-password"
                  :disabled="auth.loading"
                  required
                />
              </div>

              <div class="d-grid">
                <button type="submit" class="btn btn-primary" :disabled="auth.loading">
                  <span v-if="auth.loading" class="spinner-border spinner-border-sm me-2"></span>
                  Se connecter
                </button>
              </div>
            </form>

            <div class="text-center mt-3 small">
              <router-link to="/register" class="text-decoration-none">
                Créer un compte
              </router-link>
              •
              <router-link to="/forgot-password" class="text-decoration-none">
                Mot de passe oublié
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
