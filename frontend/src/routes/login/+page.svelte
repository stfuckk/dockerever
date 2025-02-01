<script>
    import AuthForm from '$lib/users/AuthForm.svelte';
    import { isUserAuthorized } from '$lib/api/auth';
    import { afterNavigate, goto } from '$app/navigation';

    async function checkAuthorization() {
        const result = await isUserAuthorized();
        if (result) goto('/');
    }

    afterNavigate(async () => {
        await checkAuthorization();
    });
</script>

<AuthForm />
