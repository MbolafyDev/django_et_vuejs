<!-- frontend/src/views/auth/RegisterView.vue -->
<script setup lang="ts">
import { computed, ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();

const form = ref({
  first_name: "",
  last_name: "",
  username: "",
  email: "",
  password: "",
});

const error = ref<string | null>(null);
const showPassword = ref(false);

const canSubmit = computed(() => {
  return (
    !!form.value.first_name.trim() &&
    !!form.value.last_name.trim() &&
    !!form.value.username.trim() &&
    !!form.value.email.trim() &&
    !!form.value.password &&
    !auth.loading
  );
});

const submit = async () => {
  error.value = null;
  try {
    await auth.register(form.value);
    router.push("/login");
  } catch (e: any) {
    const data = e?.response?.data;
    error.value =
      data?.detail ||
      data?.non_field_errors?.[0] ||
      data?.first_name?.[0] ||
      data?.last_name?.[0] ||
      data?.username?.[0] ||
      data?.email?.[0] ||
      data?.password?.[0] ||
      (data ? JSON.stringify(data) : null) ||
      e?.message ||
      "Erreur lors de l'inscription";
  }
};
</script>

<template>
  <div class="zs-dashboard zs-auth">
    <div class="container py-4">
      <div class="row justify-content-center">
        <div class="col-12 col-md-10 col-lg-8 col-xl-7">
          <div class="zs-card">
            <!-- Title -->
            <div class="text-center mb-5 my-2">
              <h3 class="mb-1 zs-title">Inscription</h3>
              <div class="text-muted small">Créez votre compte et accédez au backoffice</div>
            </div>

            <div v-if="error" class="alert alert-danger py-2">
              <i class="fa-solid fa-triangle-exclamation me-1"></i>
              {{ error }}
            </div>

            

            <form @submit.prevent="submit" class="row g-3">
              <div class="col-12 col-md-6">
                <label class="form-label small mb-1">Prénom</label>
                <div class="input-group input-group-sm">
                  <span class="input-group-text bg-white">
                    <i class="fa-solid fa-id-card"></i>
                  </span>
                  <input
                    v-model="form.first_name"
                    type="text"
                    class="form-control"
                    placeholder="Votre prénom"
                    autocomplete="given-name"
                    :disabled="auth.loading"
                    required
                  />
                </div>
              </div>

              <div class="col-12 col-md-6">
                <label class="form-label small mb-1">Nom</label>
                <div class="input-group input-group-sm">
                  <span class="input-group-text bg-white">
                    <i class="fa-solid fa-id-card-clip"></i>
                  </span>
                  <input
                    v-model="form.last_name"
                    type="text"
                    class="form-control"
                    placeholder="Votre nom"
                    autocomplete="family-name"
                    :disabled="auth.loading"
                    required
                  />
                </div>
              </div>

              <div class="col-12 col-md-6">
                <label class="form-label small mb-1">Nom d’utilisateur</label>
                <div class="input-group input-group-sm">
                  <span class="input-group-text bg-white">
                    <i class="fa-solid fa-at"></i>
                  </span>
                  <input
                    v-model="form.username"
                    type="text"
                    class="form-control"
                    placeholder="ex: jocelin"
                    autocomplete="username"
                    :disabled="auth.loading"
                    required
                  />
                </div>
              </div>

              <div class="col-12 col-md-6">
                <label class="form-label small mb-1">Email</label>
                <div class="input-group input-group-sm">
                  <span class="input-group-text bg-white">
                    <i class="fa-regular fa-envelope"></i>
                  </span>
                  <input
                    v-model="form.email"
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
                    v-model="form.password"
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
                 <div class="text-muted small">
                  Déjà un compte ?
                  <router-link to="/login" class="text-decoration-none fw-semibold">
                    Se connecter
                  </router-link>
                </div>

                <button class="btn btn-sm btn-primary" type="submit" :disabled="!canSubmit">
                  <span v-if="auth.loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="fa-solid fa-user-plus me-2"></i>
                  Créer un compte
                </button>
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

/* ✅ mêmes détails inputs que login */
.input-group-text {
  border-right: 0;
}
.input-group .form-control {
  border-left: 0;
}
</style>
