<script>
    import { Navbar, NavBrand, NavLi, NavUl, NavHamburger, Dropdown, DropdownItem, DropdownDivider, DarkMode } from 'flowbite-svelte';
    import { ChevronDownOutline } from 'flowbite-svelte-icons';
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { is_authorized } from '$lib/stores/authStore';
    import { goto } from '$app/navigation';
    import { get } from 'svelte/store';

    $: activeUrl = $page.url.pathname;
    function handleLogout() {
        is_authorized.set(false);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        goto('/login');
    }

    function checkUserAuth(event, path) {
        if (!get(is_authorized)) {
            event.preventDefault();
            goto('/login');
        } else {
            goto(path); // кастомный переход
        }
    }
</script>
  

<Navbar class="border-b">
    <NavBrand class="cursor-default">
        <span class="self-center whitespace-nowrap text-xl font-semibold dark:text-white border-b" >DockerEver</span>
    </NavBrand>
    <NavHamburger />
    <NavUl {activeUrl}>
        <NavLi class="mt-2 cursor-pointer" on:click={(e) => checkUserAuth(e, '/')} active={true}>Главная</NavLi>
            {#if $is_authorized}
                <NavLi class="mt-2 cursor-pointer">
                    Настройки<ChevronDownOutline class="w-6 h-6 ms-1 text-primary-800 dark:text-white inline" />
                </NavLi>
                <Dropdown class="w-44 z-20">
                    <DropdownItem on:click={(e) => checkUserAuth(e, '/profile')}>Профиль</DropdownItem>
                    <DropdownItem on:click={(e) => checkUserAuth(e, '/users')}>Пользователи и права</DropdownItem>
                    <DropdownDivider />
                    <DropdownItem on:click={handleLogout}>Выйти</DropdownItem>
                </Dropdown>
            {/if}
            <DropdownDivider />
            <DarkMode/>
        </NavUl>
</Navbar>