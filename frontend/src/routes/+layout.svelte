<script>
    import '../app.css';
    import NavigationBar from '$lib/global/NavigationBar.svelte';
    import { isAuthorized, userData } from '$lib/stores/authStore';
    import { onMount } from 'svelte';
    import { isUserAuthorized, getUserData } from '$lib/api/auth';
    import { goto } from "$app/navigation";
    import { page } from '$app/stores';

    let token;

    async function checkAuthorization() {
        const result = await isUserAuthorized();
        isAuthorized.set(result);
        if ($isAuthorized) {
            const data = await getUserData();
            $userData.set(data)
        }

        if (!result && $page.url.pathname !== '/contact')
            goto('/login');
    }

    onMount(() => {
        const unsubscribe = page.subscribe(() => {
            checkAuthorization();
        });

        return () => {
            unsubscribe();
        };
    });


    let { children } = $props();
    
</script>

<NavigationBar />

{@render children()}