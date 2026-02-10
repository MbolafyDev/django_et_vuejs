import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },

  // 🔥 PROXY DEV → BACKEND DJANGO
  server: {
    host: "localhost",
    port: 5173,

    proxy: {
      // API Django (DRF)
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false,
      },

      // Fichiers media (logos, signatures, images facture, etc.)
      "/media": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false,
      },

      // (optionnel) fichiers statiques si tu les exposes en dev
      "/static": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
