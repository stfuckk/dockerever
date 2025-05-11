<script>
  import { Card, Button, Label, Input, Helper } from "flowbite-svelte";
  import { changePassword, getCurrentUser } from "$lib/api/auth";
  import { is_authorized, user } from "$lib/stores/authStore";
  import { goto } from "$app/navigation";
  import { error } from "$lib/stores/authStore";
  import { get } from "svelte/store";
  import { EyeOutline, EyeSlashOutline } from "flowbite-svelte-icons";

  export let token;
  export let username = "";
  let show1 = false;
  let show2 = false;
  let newPassword = "";
  let prevPassword = "";
  let loading = false;

  async function handleSubmit(event) {
    event.preventDefault();
    loading = true;
    error.set(null);
    try {
      if (!username) {
        goto("/");
        return;
      }

      await changePassword(
        {
          username: username,
          password: newPassword,
          prev_password: prevPassword,
        },
        token
      );

      const updatedUser = await getCurrentUser();
      user.set(updatedUser);
      is_authorized.set(true);
      goto("/");
    } catch (err) {
      error.set(err.message);
    } finally {
      loading = false;
    }
  }
</script>

<div class="flex justify-center mt-32">
  <Card>
    <form class="flex flex-col space-y-6" on:submit={handleSubmit}>
      <h3 class="text-xl font-medium text-gray-900 dark:text-white">
        Задайте новый пароль, отличный от старого
      </h3>
      <Label class="space-y-2">
        <span>Текущий пароль</span>
        <Input
          type={show1 ? "text" : "password"}
          bind:value={prevPassword}
          on:input={() => error.set(null)}
          disabled={loading}
          placeholder="•••••••••"
          required
        >
          <button
            type="button"
            slot="right"
            on:click={() => (show1 = !show1)}
            class="pointer-events-auto"
          >
            {#if show1}
              <EyeOutline class="w-6 h-6" />
            {:else}
              <EyeSlashOutline class="w-6 h-6" />
            {/if}
          </button>
        </Input>
      </Label>
      <Label class="space-y-2">
        <span>Новый пароль</span>
        <Input
          type={show2 ? "text" : "password"}
          bind:value={newPassword}
          on:input={() => error.set(null)}
          disabled={loading}
          placeholder="•••••••••"
          required
        >
          <button
            type="button"
            slot="right"
            on:click={() => (show2 = !show2)}
            class="pointer-events-auto"
          >
            {#if show2}
              <EyeOutline class="w-6 h-6" />
            {:else}
              <EyeSlashOutline class="w-6 h-6" />
            {/if}
          </button>
        </Input>
      </Label>
      <Button type="submit" disabled={loading} class="w-full"
        >Сменить пароль</Button
      >
      {#if $error}
        <Helper class="flex justify-center text-sm" color="red">
          <span class="font-medium">{$error}</span>
        </Helper>
      {/if}
    </form>
  </Card>
</div>
