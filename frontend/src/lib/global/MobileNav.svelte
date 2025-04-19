<script>
    import { page } from '$app/stores';
    import { BottomNav, BottomNavItem } from 'flowbite-svelte';
    import {
      ChartPieSolid,
      GridPlusSolid,
      DatabaseSolid,
      ShareNodesSolid,
      LayersSolid
    } from 'flowbite-svelte-icons';
  
    $: active = $page.url.pathname;
  </script>
  
  <BottomNav position="fixed" class="md:hidden bottom-0 left-0 w-full" classInner="grid-cols-5">
    <BottomNavItem btnName="Дашборды" href="/dashboards" active={active === '/dashboards'}>
      <ChartPieSolid class="w-6 h-6 mb-1" />
    </BottomNavItem>
    <BottomNavItem btnName="Контейнеры" href="/containers" active={active === '/containers'}>
      <GridPlusSolid class="w-6 h-6 mb-1" />
    </BottomNavItem>
    <BottomNavItem btnName="Образы" href="/images" active={active === '/images'}>
      <DatabaseSolid class="w-6 h-6 mb-1" />
    </BottomNavItem>
    <BottomNavItem btnName="Сети" href="/networks" active={active === '/networks'}>
      <ShareNodesSolid class="w-6 h-6 mb-1" />
    </BottomNavItem>
    <BottomNavItem btnName="Вольюмы" href="/volumes" active={active === '/volumes'}>
      <LayersSolid class="w-6 h-6 mb-1" />
    </BottomNavItem>
  </BottomNav>
  