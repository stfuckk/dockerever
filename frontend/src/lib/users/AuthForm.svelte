<script>
    import { Card, Button, Label, Input, Checkbox, Helper } from 'flowbite-svelte';
    import { loginUser, changePassword } from '$lib/api/auth';
    import { error, is_authorized } from '$lib/stores/authStore';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import ChangePassword from '$lib/users/ChangePassword.svelte';

    let username = '';
    let password = '';
    let loading = false;
    let mustChange = false;
    let accessToken = '';

    async function handleSubmit(event) {
        event.preventDefault();
        loading = true;
        error.set(null);
        try {
            const res = await loginUser({username, password});
            if (res.must_change_password) {
              mustChange = true;
              accessToken = res.access_token;
            } else {
              goto('/')
            }
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

{#if mustChange}
  <ChangePassword token={accessToken} username={username}/>
{:else}
  <div class="flex justify-center mt-4">
    <Card>
      <form class="flex flex-col space-y-6" on:submit|preventDefault={handleSubmit}>
        <h3 class="text-xl font-medium text-gray-900 dark:text-white">Вход в систему</h3>
        <Label class="space-y-2">
          <span>Логин</span>
          <Input type="text" bind:value={username} on:input={clearError} disabled={loading} placeholder="Ваш логин" required />
        </Label>
        <Label class="space-y-2">
          <span>Пароль</span>
          <Input type="password" bind:value={password} on:input={clearError} disabled={loading} placeholder="•••••••••" required />
        </Label>
        <Button type="submit" disabled={loading} class="w-full">Войти</Button>
        {#if $error}
          <Helper class="flex justify-center text-sm" color="red">
            <span class="font-medium">{$error}</span>
          </Helper>
        {/if}
      </form>
    </Card>
  </div>
{/if}

  