<script>
    import { onMount } from 'svelte';
    import { isAuthorized, error, userData } from '$lib/stores/authStore';
</script>

{#if $isAuthorized && $userData}
    <h1 class="text-md tracking-tight text-gray-900 dark:text-white">Привет, {$userData.first_name}!</h1>
{:else}
    <p class="text-md tracking-tight text-gray-900 dark:text-white">Пожалуйста, войдите в систему.</p>
{/if}