import { onMounted, ref } from "vue";
import { useFacturation } from "@/composables/facturation/useFacturation";
import { formatMoney } from "@/utils/format";

export function useFacturesView() {
  const f = useFacturation();

  const viewMode = ref<"table" | "card">("table");

  // auto-load (comme VenteDashboard)
  onMounted(() => {
    f.load();
  });

  return {
    ...f,
    viewMode,
    formatMoney,
  };
}
