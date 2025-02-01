<script>
    import '../app.css';
    import NavigationBar from '$lib/global/NavigationBar.svelte';
    import { isAuthorized } from '$lib/stores/authStore';
    import { onMount } from 'svelte';
    import { isUserAuthorized } from '$lib/api/auth';
    import { afterNavigate, goto } from "$app/navigation";
    import { page } from '$app/stores';

    async function checkAuthorization() {
        const result = await isUserAuthorized();
        isAuthorized.set(result);

        if (!result) goto('/login');
    }

    afterNavigate(async () => {
        if (!$page.url.toString().includes("/login")) {
            await checkAuthorization();
        }
    });

    let { children } = $props();
    
</script>

<NavigationBar />

{@render children()}