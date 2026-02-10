<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../../stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const new_password = ref("");
const error = ref("");

const submit = async () => {
  error.value = "";
  try {
    await auth.resetPassword(
      route.query.uid,
      route.query.token,
      new_password.value
    );
    router.push("/login");
  } catch (e) {
    error.value = "Lien invalide ou expiré";
  }
};
</script>

<template>
  <div class="container min-vh-100 d-flex align-items-center justify-content-center">
    <div class="row w-100 justify-content-center">
      <div class="col-12 col-sm-10 col-md-6 col-lg-4">
        <div class="card shadow-sm">
          <div class="card-body">

            <h4 class="card-title text-center mb-3">Nouveau mot de passe</h4>

            <div v-if="error" class="alert alert-danger py-2">
              {{ error }}
            </div>

            <form @submit.prevent="submit">
              <div class="mb-3">
                <label class="form-label">Nouveau mot de passe</label>
                <input
                  v-model="new_password"
                  type="password"
                  class="form-control"
                  placeholder="••••••••"
                  autocomplete="new-password"
                  required
                />
              </div>

              <div class="d-grid">
                <button type="submit" class="btn btn-primary">
                  Réinitialiser
                </button>
              </div>
            </form>

            <div class="text-center mt-3 small">
              <a href="/login" class="text-decoration-none">
                Retour à la connexion
              </a>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>
