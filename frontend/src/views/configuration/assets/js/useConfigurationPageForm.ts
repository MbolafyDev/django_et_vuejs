import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ConfigurationAPI } from "@/services/configuration";

export function useConfigurationPageForm(props: { mode: "create" | "edit"; id?: number }) {
  const router = useRouter();

  const loading = ref(false);
  const saving = ref(false);
  const error = ref("");

  const nom = ref("");
  const lien = ref("");

  const logoFile = ref<File | null>(null);
  const logoPreview = ref<string | null>(null);

  function back() {
    router.push({ name: "configuration_pages" });
  }

  function onFile(e: Event) {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0] || null;
    logoFile.value = file;
    logoPreview.value = file ? URL.createObjectURL(file) : null;
  }

  async function load() {
    if (props.mode !== "edit" || !props.id) return;

    loading.value = true;
    error.value = "";
    try {
      const res = await ConfigurationAPI.getPage(props.id);
      const p = res.data as any;

      nom.value = p.nom || "";
      lien.value = p.lien || "";
      logoPreview.value = p.logo_url || null;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || "Erreur chargement page";
    } finally {
      loading.value = false;
    }
  }

  async function save() {
    error.value = "";

    if (!nom.value.trim()) { error.value = "Nom obligatoire"; return; }
    if (!lien.value.trim()) { error.value = "Lien obligatoire"; return; }

    saving.value = true;
    try {
      const fd = new FormData();
      fd.append("nom", nom.value.trim());
      fd.append("lien", lien.value.trim());
      if (logoFile.value) fd.append("logo", logoFile.value);

      if (props.mode === "create") {
        await ConfigurationAPI.createPage(fd);
      } else {
        await ConfigurationAPI.updatePage(props.id!, fd);
      }
      back();
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
    router,
    loading,
    saving,
    error,
    nom,
    lien,
    logoFile,
    logoPreview,
    back,
    onFile,
    load,
    save,
  };
}
