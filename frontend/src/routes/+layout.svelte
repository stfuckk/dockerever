<script>
    import '../app.css';
    import NavigationBar from '$lib/global/NavigationBar.svelte';
    import { isAuthorized as authCheck } from '$lib/api/auth';
    import { is_authorized, user } from '$lib/stores/authStore';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { get } from 'svelte/store';
  
    let { children } = $props();
  
    onMount(async () => {
        const path = get(page).url.pathname;
        const currentUser = await authCheck();
      
        if (!currentUser) {
            is_authorized.set(false);
            goto('/login');
            return;
        }
        
        if (currentUser.must_change_password) {
            goto('/login?reason=must_change_password');
            return;
        }
        
        user.set(currentUser);
        is_authorized.set(true);
    });
  </script>
  
  <NavigationBar />
  {@render children()}
  