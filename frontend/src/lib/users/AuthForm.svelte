<script>
    import { Card, Button, Label, Input, Checkbox, Helper } from 'flowbite-svelte';
    import { loginUser } from '$lib/api/auth';
    import { error, isAuthorized } from '$lib/stores/authStore';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    let username = '';
    let password = '';
    let loading = false;

    async function handleSubmit(event) {
        event.preventDefault();
        loading = true;
        try {
            const token = await loginUser(username, password);
            if (token) {
                goto('/') 
            };
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
    <form class="flex flex-col space-y-6" action="/" on:submit={handleSubmit}>
        <h3 class="text-xl font-medium text-gray-900 dark:text-white">Вход в систему</h3>
        <Label class="space-y-2">
        <span>Логин</span>
        <Input type="text" bind:value={username} on:input={clearError} disabled={loading} name="text" placeholder="Ваш логин" required />
        </Label>
        <Label class="space-y-2">
        <span>Пароль</span>
        <Input type="password" bind:value={password} on:input={clearError} disabled={loading} name="password" placeholder="•••••••••" required />
        </Label>
        <Button type="submit" disabled={loading} class="w-full">Войти</Button>
            {#if $error}
            <Helper class='flex justify-center text-sm' color='red'>
                <span class="font-medium">{$error}</span>
            </Helper>
            {/if}
    </form>
    </Card>
</div>

  