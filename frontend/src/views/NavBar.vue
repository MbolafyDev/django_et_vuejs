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
  <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom shadow-sm">
    <div class="container-fluid">

      <!-- LOGO -->
      <router-link to="/" class="navbar-brand fw-bold text-primary">
        <img
          src="/logo.png"
          alt="Logo"
          height="32"
          class="me-2"
        />
        MonApp
      </router-link>

      <!-- TOGGLER -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#mainNavbar"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- MENU -->
      <div class="collapse navbar-collapse" id="mainNavbar">

        <!-- LEFT MENU -->
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item"><router-link class="nav-link" to="/commandes">Commandes</router-link></li>
          <li class="nav-item"><router-link class="nav-link" to="/facturation">Facturation</router-link></li>
          <li class="nav-item"><router-link class="nav-link" to="/encaissement">Encaissement</router-link></li>
          <li class="nav-item"><router-link class="nav-link" to="/livraison">Livraison</router-link></li>
          <li class="nav-item"><router-link class="nav-link" to="/achat">Achat</router-link></li>
          <li class="nav-item"><router-link class="nav-link" to="/articles">Articles</router-link></li>
          <li class="nav-item"><router-link class="nav-link" to="/clients">Clients</router-link></li>
          <li class="nav-item"><router-link class="nav-link" to="/parametres">Paramètres</router-link></li>
        </ul>

        <!-- RIGHT AUTH -->
        <div class="d-flex align-items-center gap-2">

          <!-- NON CONNECTÉ -->
          <template v-if="!auth.isAuthenticated">
            <router-link to="/register" class="btn btn-outline-primary">
              Inscription
            </router-link>
            <router-link to="/login" class="btn btn-primary">
              Connexion
            </router-link>
          </template>

          <!-- CONNECTÉ -->
          <template v-else>
            <span class="me-2 text-muted">
              👋 {{ auth.user?.username }}
            </span>
            <button class="btn btn-danger btn-sm" @click="logout">
              Déconnexion
            </button>
          </template>

        </div>

      </div>
    </div>
  </nav>
</template>
