<script>
    import '../app.css';
    import NavigationBar from '$lib/global/NavigationBar.svelte';
    import { isAuthorized } from '$lib/stores/authStore';
    import { onMount } from 'svelte';
    import { isUserAuthorized } from '$lib/api/auth';
    import { goto } from "$app/navigation";
    import { page } from '$app/stores';

    onMount(() => {
        const token = localStorage.getItem("token");
        async function checkAuthorization() {
            if (token) {
                const result = await isUserAuthorized(token);
                isAuthorized.set(result);

                if (!result && $page.url.pathname !== '/contact')
                    goto('/login');
            } else if ($page.url.pathname !== '/contact') goto('/login');
        }
        checkAuthorization();
    });

    let { children } = $props();
    
</script>

<NavigationBar />

{@render children()}