import { ref, onMounted } from "vue";
import { ConfigurationAPI } from "@/services/configuration";

export function useConfigurationDashboard() {
  const loading = ref(false);
  const saving = ref(false);

  const app_name = ref("");
  const maintenance_mode = ref(false);
  const maintenance_message = ref("");

  const error = ref("");
  const success = ref("");

  async function load() {
    loading.value = true;
    error.value = "";
    try {
      const res = await ConfigurationAPI.getSolo();
      const data = res.data;

      app_name.value = data.app_name || "";
      maintenance_mode.value = !!data.maintenance_mode;
      maintenance_message.value = data.maintenance_message || "";
    } catch (e: any) {
      error.value = e?.response?.data?.detail || "Erreur chargement configuration";
    } finally {
      loading.value = false;
    }
  }

  async function save() {
    saving.value = true;
    error.value = "";
    success.value = "";
    try {
      await ConfigurationAPI.patchSolo({
        app_name: app_name.value,
        maintenance_mode: maintenance_mode.value,
        maintenance_message: maintenance_message.value,
      });
      success.value = "Configuration enregistrée.";
    } catch (e: any) {
      error.value =
        e?.response?.data?.detail ||
        JSON.stringify(e?.response?.data || e) ||
        "Erreur sauvegarde";
    } finally {
      saving.value = false;
    }
  }

  onMounted(load);

  return {
    loading,
    saving,
    app_name,
    maintenance_mode,
    maintenance_message,
    error,
    success,
    load,
    save,
  };
}
