<script>
  import { Card, Button, Label, Input, Helper } from 'flowbite-svelte';
  import { changePassword, getCurrentUser } from '$lib/api/auth';
  import { is_authorized, user } from '$lib/stores/authStore';
  import { goto } from '$app/navigation';
  import { error } from '$lib/stores/authStore';
  import { get } from 'svelte/store';

  export let token;
  export let username = '';
  let newPassword = '';
  let prevPassword = '';
  let loading = false;
  
  async function handleSubmit(event) {
    event.preventDefault();
    loading = true;
    error.set(null);
    try {
      if (!username) {
        goto('/')
        return
      }

      await changePassword({
        username: username,
        password: newPassword,
        prev_password: prevPassword
      }, token);

      const updatedUser = await getCurrentUser();
      user.set(updatedUser);
      is_authorized.set(true);
      goto('/');
    } catch (err) {
      error.set(err.message);
    } finally {
      loading = false;
    }
  }

  function clearError() {
    error.set(null);
  }
  </script>

  <div class="flex justify-center mt-4">
    <Card>
      <form class="flex flex-col space-y-6" on:submit={handleSubmit}>
        <h3 class="text-xl font-medium text-gray-900 dark:text-white">Задайте новый пароль, отличный от старого</h3>
        <Label class="space-y-2">
          <span>Текущий пароль</span>
          <Input type="password" bind:value={prevPassword} on:input={clearError} disabled={loading} placeholder="•••••••••" required />
        </Label>
        <Label class="space-y-2">
          <span>Новый пароль</span>
          <Input type="password" bind:value={newPassword} on:input={clearError} disabled={loading} placeholder="•••••••••" required />
        </Label>
        <Button type="submit" disabled={loading} class="w-full">Сменить пароль</Button>
        {#if $error}
          <Helper class="flex justify-center text-sm" color="red">
            <span class="font-medium">{$error}</span>
          </Helper>
        {/if}
      </form>
    </Card>
  </div>
