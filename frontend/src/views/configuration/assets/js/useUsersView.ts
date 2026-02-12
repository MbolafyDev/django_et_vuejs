import { computed, onMounted, ref } from "vue";
import Modal from "bootstrap/js/dist/modal";
import { ConfigUsersAPI, type UserItem, type UserRole } from "@/services/configuration_users";
import { useAuthStore } from "@/stores/auth";

export function useUsersView() {
  const auth = useAuthStore();
  const isAdmin = computed(
    () => auth.user?.role === "ADMIN" || (auth.user as any)?.is_staff || (auth.user as any)?.is_superuser
  );

  const q = ref("");
  const role = ref<string>("");
  const actif = ref<string>("");

  const loading = ref(false);
  const items = ref<UserItem[]>([]);
  const errorMsg = ref<string>("");

  const roles: Array<{ value: UserRole; label: string }> = [
    { value: "ADMIN", label: "Admin" },
    { value: "UTILISATEUR", label: "Utilisateur" },
    { value: "COMMERCIALE", label: "Commerciale" },
    { value: "COMMUNITY_MANAGER", label: "Community manager" },
  ];

  const selected = ref<UserItem | null>(null);
  const editRole = ref<UserRole>("COMMERCIALE");
  const editActive = ref(true);

  function badgeClass(u: UserItem) {
    if (!u.is_active) return "badge text-bg-danger";
    if (u.role === "ADMIN") return "badge text-bg-primary";
    if (u.role === "UTILISATEUR") return "badge text-bg-success";
    return "badge text-bg-secondary";
  }

  function roleLabel(r: string) {
    return roles.find((x) => x.value === (r as any))?.label || r;
  }

  async function load() {
    loading.value = true;
    errorMsg.value = "";
    try {
      const res = await ConfigUsersAPI.list({
        q: q.value || undefined,
        role: (role.value as any) || undefined,
        actif: (actif.value as any) || undefined,
        page_size: 200,
      });
      const data: any = res.data;
      items.value = data?.results || data || [];
    } catch (e: any) {
      items.value = [];
      errorMsg.value = e?.response?.data?.detail || "Erreur lors du chargement des utilisateurs.";
    } finally {
      loading.value = false;
    }
  }

  function openEdit(u: UserItem) {
    selected.value = u;
    editRole.value = u.role;
    editActive.value = u.is_active;

    const el = document.getElementById("zsUserModal");
    if (!el) return;

    Modal.getOrCreateInstance(el).show();
  }

  async function saveEdit() {
    if (!selected.value) return;

    const id = selected.value.id;
    loading.value = true;
    errorMsg.value = "";

    try {
      await ConfigUsersAPI.setStatus(id, editActive.value);

      if (editRole.value !== selected.value.role) {
        await ConfigUsersAPI.setRole(id, editRole.value);
      }

      await load();

      const el = document.getElementById("zsUserModal");
      if (el) Modal.getInstance(el)?.hide();
    } catch (e: any) {
      errorMsg.value =
        e?.response?.data?.detail ||
        (typeof e?.response?.data === "string" ? e.response.data : "") ||
        "Impossible de mettre à jour cet utilisateur.";
    } finally {
      loading.value = false;
    }
  }

  onMounted(load);

  return {
    auth,
    isAdmin,
    q,
    role,
    actif,
    loading,
    items,
    errorMsg,
    roles,
    selected,
    editRole,
    editActive,
    badgeClass,
    roleLabel,
    load,
    openEdit,
    saveEdit,
  };
}
