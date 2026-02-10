<script setup>
import { ref } from "vue";
import { useAuthStore } from "../../stores/auth";

const auth = useAuthStore();
const email = ref("");
const message = ref("");
const error = ref("");

const submit = async () => {
  message.value = "";
  error.value = "";
  try {
    const res = await auth.forgotPassword(email.value);
    message.value =
      res?.data?.message || "Si l'email existe, un lien a été envoyé.";
  } catch (e) {
    error.value = "Une erreur est survenue. Veuillez réessayer.";
  }
};
</script>

<template>
  <div class="container min-vh-100 d-flex align-items-center justify-content-center">
    <div class="row w-100 justify-content-center">
      <div class="col-12 col-sm-10 col-md-6 col-lg-4">
        <div class="card shadow-sm">
          <div class="card-body">

            <h4 class="card-title text-center mb-3">Mot de passe oublié</h4>

            <div v-if="error" class="alert alert-danger py-2">
              {{ error }}
            </div>

            <div v-if="message" class="alert alert-success py-2">
              {{ message }}
            </div>

            <form @submit.prevent="submit">
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input
                  v-model="email"
                  type="email"
                  class="form-control"
                  placeholder="Entrez votre email"
                  autocomplete="email"
                  required
                />
              </div>

              <div class="d-grid">
                <button type="submit" class="btn btn-primary">
                  Envoyer le lien
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
