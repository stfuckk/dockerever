<script>
    import AuthForm from '$lib/users/AuthForm.svelte';
    import { isAuthorized } from '$lib/stores/authStore';
</script>

{#if !$isAuthorized}
    <AuthForm />
{/if}