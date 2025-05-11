<script>
  import { onMount } from "svelte";
  import { assignUserRole, removeUserRole, getAllRoles } from "$lib/api/users";
  import { Checkbox } from "flowbite-svelte";

  export let user;
  let roles = [];

  function hasRole(roleName) {
    return user.roles.some((r) => r.name === roleName);
  }

  async function toggleRole(role, checked) {
    try {
      if (checked) {
        await assignUserRole(user.id, role.id);
      } else {
        await removeUserRole(user.id, role.id);
      }
    } catch (err) {
      console.error("Ошибка при изменении роли:", err);
    }
  }

  onMount(async () => {
    try {
      roles = await getAllRoles();
    } catch (err) {
      console.error("Ошибка загрузки ролей:", err);
    }
  });
</script>

{#each roles as role}
  <div class="flex items-center gap-2">
    <Checkbox
      checked={hasRole(role.name)}
      on:change={(e) => toggleRole(role, e.target.checked)}
    />
    <span>{role.name}</span>
  </div>
{/each}
