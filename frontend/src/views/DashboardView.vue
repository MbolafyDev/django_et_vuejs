<!-- frontend/src/views/DashboardView.vue -->
<script setup>
import AppNavbar from "../components/AppNavbar.vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
</script>

<template>
  <div>
    <AppNavbar />

    <div class="container py-4">
      <div class="card shadow-sm">
        <div class="card-body text-center">
          <h3 class="mb-3">
            Bonjour <span class="text-primary">{{ auth.user?.username }}</span>
          </h3>

          <p class="text-muted mb-0">
            Votre adresse email :
            <strong>{{ auth.user?.email }}</strong>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
