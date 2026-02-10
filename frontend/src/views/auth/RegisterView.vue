<script setup>
import { ref } from "vue";
import { useAuthStore } from "../../stores/auth";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();

const form = ref({
  username: "",
  email: "",
  password: "",
});

const error = ref("");

const submit = async () => {
  error.value = "";
  try {
    await auth.register(form.value);
    router.push("/login");
  }  catch (e) {
    console.log("REGISTER FULL:", e);
    console.log("REGISTER status:", e?.response?.status);
    console.log("REGISTER data:", e?.response?.data);

    const data = e?.response?.data;

    error.value =
        (data?.detail) ||
        (data?.non_field_errors?.[0]) ||
        (data?.username?.[0]) ||
        (data?.email?.[0]) ||
        (data?.password?.[0]) ||
        (data ? JSON.stringify(data) : null) ||
        e?.message ||
        "Erreur lors de l'inscription";
    }
};
</script>

<template>
  <div class="container min-vh-100 d-flex align-items-center justify-content-center">
    <div class="row w-100 justify-content-center">
      <div class="col-12 col-sm-10 col-md-6 col-lg-4">
        <div class="card shadow-sm">
          <div class="card-body">

            <h4 class="card-title text-center mb-3">Inscription</h4>

            <div v-if="error" class="alert alert-danger py-2">
              {{ error }}
            </div>

            <form @submit.prevent="submit">
              <div class="mb-3">
                <label class="form-label">Nom d’utilisateur</label>
                <input
                  v-model="form.username"
                  type="text"
                  class="form-control"
                  placeholder="Votre nom d’utilisateur"
                  autocomplete="username"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Email</label>
                <input
                  v-model="form.email"
                  type="email"
                  class="form-control"
                  placeholder="ex: nom@gmail.com"
                  autocomplete="email"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Mot de passe</label>
                <input
                  v-model="form.password"
                  type="password"
                  class="form-control"
                  placeholder="••••••••"
                  autocomplete="new-password"
                  required
                />
              </div>

              <div class="d-grid">
                <button type="submit" class="btn btn-primary">
                  Créer un compte
                </button>
              </div>
            </form>

            <div class="text-center mt-3 small">
              <a href="/login" class="text-decoration-none">
                Déjà un compte ? Se connecter
              </a>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>
