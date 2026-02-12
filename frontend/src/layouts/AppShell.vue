<!-- frontend/src/layouts/AppShell.vue -->
<script setup lang="ts">
import AppNavbar from "@/components/AppNavbar.vue";
</script>

<template>
  <div class="zs-app-shell">
    <AppNavbar />

    <!-- zone page -->
    <main class="zs-app-main">
      <router-view />
    </main>
  </div>
</template>

<style>
/* évite que le contenu colle au navbar sticky */
.zs-app-main {
  padding-top: 8px;
}
</style>
