<script>
    import AuthForm from '$lib/users/AuthForm.svelte';
    import { isAuthorized } from '$lib/stores/authStore';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
</script>

{#if !$isAuthorized}
    <AuthForm />
{/if}