<script>
  import { Checkbox } from "flowbite-svelte";
  import { assignUserRole, removeUserRole } from "$lib/api/users";

  export let user;
  export let roles = [];

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
