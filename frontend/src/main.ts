import { createApp } from "vue";
import { createPinia } from "pinia";

import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import "./assets/main.css";
import "@fortawesome/fontawesome-free/css/all.min.css";
import "@/assets/pages/facturation.css";

import App from "./App.vue";
import router from "./router";
import { useAuthStore } from "./stores/auth";

const app = createApp(App);

const pinia = createPinia();
app.use(pinia);

// ✅ init session AVANT router
const auth = useAuthStore();
auth.initFromStorage().catch(() => {
  auth.logoutLocalOnly();
});

app.use(router);
app.mount("#app");
