<script>
    import AuthForm from '$lib/users/AuthForm.svelte';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { is_authorized, user } from '$lib/stores/authStore';
    import Toast from '$lib/global/Toast.svelte';
    import { get } from 'svelte/store';
    import { page } from '$app/stores';

    let showToast = false;

    onMount(() => {
        let authorized = get(is_authorized);
        let currentUser = get(user);

        if (authorized && !currentUser?.must_change_password) {
            goto('/');
        }

        const url = get(page).url;
        if (url.searchParams.get('reason') === 'must_change_password') {
            showToast = true;
        }
    });
</script>

{#if showToast}
    <Toast message="Вы должны сменить пароль перед использованием системы."/>
{/if}
<AuthForm />
