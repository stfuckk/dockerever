<script>
    import { page } from '$app/stores'
    import { Navbar, NavBrand, NavLi, NavUl, NavHamburger } from 'flowbite-svelte';
    import { DarkMode } from 'flowbite-svelte';
    $: activeUrl = $page.url.pathname;
</script>
  

<Navbar rounded color="form" class="fixed z-20 border-b">
    <NavBrand href="/">
        <span class="self-center whitespace-nowrap text-xl font-semibold dark:text-white">DockerEver</span>
    </NavBrand>
    <NavHamburger />
    <div class="flex items-center">
        <NavUl {activeUrl} class="flex space-x-4">
            <NavLi href="/" active={true}>Home</NavLi>
            <NavLi href="/about">About</NavLi>
        </NavUl>
        <DarkMode class="mk-4"/>
    </div>
</Navbar>