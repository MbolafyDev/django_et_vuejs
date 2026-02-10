<script setup>
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();

const logout = async () => {
  await auth.logout();
  router.push("/login");
};
</script>

<template>
  <div class="container min-vh-100 d-flex align-items-center justify-content-center">
    <div class="row w-100 justify-content-center">
      <div class="col-12 col-sm-10 col-md-8 col-lg-6">

        <div class="card shadow-sm">
          <div class="card-body text-center">

            <h3 class="mb-3">
              Bonjour <span class="text-primary">{{ auth.user?.username }}</span> 👋
            </h3>

            <p class="text-muted mb-0">
              Votre adresse email :
              <strong>{{ auth.user?.email }}</strong>
            </p>

            <div class="d-grid mt-4">
              <button class="btn btn-danger" @click="logout">
                Se déconnecter
              </button>
            </div>

          </div>
        </div>

      </div>
    </div>
  </div>
</template>
