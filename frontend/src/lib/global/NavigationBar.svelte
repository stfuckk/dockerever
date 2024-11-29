<script>
    import { Navbar, NavBrand, NavLi, NavUl, NavHamburger, Dropdown, DropdownItem, DropdownDivider, DarkMode } from 'flowbite-svelte';
    import { ChevronDownOutline } from 'flowbite-svelte-icons';
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { isAuthorized } from '$lib/stores/authStore';
    import { goto } from '$app/navigation';

    $: activeUrl = $page.url.pathname;

    function handleLogout() {
        isAuthorized.set(false);
        localStorage.removeItem('token');
        goto('/login');
    }
</script>
  

<Navbar class="border-b">
    <NavBrand href="/">
        <span class="self-center whitespace-nowrap text-xl font-semibold dark:text-white border-b">DockerEver</span>
    </NavBrand>
    <NavHamburger />
    <NavUl {activeUrl}>
        <NavLi class="mt-2" href="/" active={true}>Главная</NavLi>
            {#if $isAuthorized}
                <NavLi class="mt-2 cursor-pointer">
                    Настройки<ChevronDownOutline class="w-6 h-6 ms-1 text-primary-800 dark:text-white inline" />
                </NavLi>
                <Dropdown class="w-44 z-20">
                    <DropdownItem href="/profile">Профиль</DropdownItem>
                    <DropdownItem href="/users">Пользователи и права</DropdownItem>
                    <DropdownDivider />
                    <DropdownItem on:click={handleLogout}>Выйти</DropdownItem>
                </Dropdown>
            {/if}
            <NavLi class="mt-2" href="/contact">Контакты</NavLi>
            <DropdownDivider />
            <DarkMode/>
        </NavUl>
</Navbar>