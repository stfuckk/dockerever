<script>
  import { page } from "$app/stores";
  import {
    Sidebar,
    SidebarGroup,
    SidebarItem,
    SidebarWrapper,
    Select,
  } from "flowbite-svelte";
  import NodeSelector from "$lib/global/NodeSelector.svelte";
  import {
    ChartPieSolid,
    GridPlusSolid,
    ShareNodesSolid,
    DatabaseSolid,
    LayersSolid,
  } from "flowbite-svelte-icons";

  let selectedNode = "";
  let nodes = [];
  $: activeUrl = $page.url.pathname;
</script>

<Sidebar class="mt-12 pl-4">
  <SidebarWrapper
    class="shadow-lg rounded-xl border border-gray-200 dark:border-gray-700 overflow-y-auto h-full"
  >

    <!-- Навигация -->
    <SidebarGroup>
      <SidebarItem label="Дашборды" href="/dashboards">
        <svelte:fragment slot="icon">
          <ChartPieSolid class="w-5 h-5" />
        </svelte:fragment>
      </SidebarItem>
      <SidebarItem label="Контейнеры" href="/containers">
        <svelte:fragment slot="icon">
          <GridPlusSolid class="w-5 h-5" />
        </svelte:fragment>
      </SidebarItem>
      <SidebarItem label="Образы" href="/images">
        <svelte:fragment slot="icon">
          <DatabaseSolid class="w-5 h-5" />
        </svelte:fragment>
      </SidebarItem>
      <SidebarItem label="Сети" href="/networks">
        <svelte:fragment slot="icon">
          <ShareNodesSolid class="w-5 h-5" />
        </svelte:fragment>
      </SidebarItem>
      <SidebarItem label="Вольюмы" href="/volumes">
        <svelte:fragment slot="icon">
          <LayersSolid class="w-5 h-5" />
        </svelte:fragment>
      </SidebarItem>
    </SidebarGroup>
  </SidebarWrapper>
</Sidebar>
