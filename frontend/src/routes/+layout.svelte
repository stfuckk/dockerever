<script>
  import "../app.css";
  import NavigationBar from "$lib/global/NavigationBar.svelte";
  import SidebarLayout from "$lib/global/SidebarLayout.svelte";
  import { isAuthorized as authCheck, authFetch } from "$lib/api/auth";
  import { is_authorized, user } from "$lib/stores/authStore";
  import { selected_node } from "$lib/stores/selected_node";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import { get } from "svelte/store";
  import MobileNav from "$lib/global/MobileNav.svelte";
  import NodeSelector from "$lib/global/NodeSelector.svelte";
  import { getNodes } from "$lib/api/dashboards";

  let { children } = $props();
  let nodes = $state([]);

  onMount(async () => {
    const currentUser = await authCheck();

    if (!currentUser) {
      is_authorized.set(false);
      goto("/login");
      return;
    }

    if (currentUser.must_change_password) {
      is_authorized.set(false);
      goto("/login?reason=must_change_password");
      return;
    }

    user.set(currentUser);
    is_authorized.set(true);
    nodes = await getNodes();

    // Загрузка из localStorage или первый из списка
    const saved = localStorage.getItem("selected_node");
    if (!saved) {
      localStorage.setItem("selected_node", JSON.stringify(nodes[0]));
    }
    selected_node.set(JSON.parse(saved));
  });
</script>

<NavigationBar />

<!-- Desktop NodeSelector -->
{#if $is_authorized}
  <div class="mt-16 md:mt-24 z-[9998] px-4">
    <NodeSelector {nodes} />
  </div>

  <!-- Mobile nav -->
  <div class="md:hidden">
    <MobileNav />
  </div>
{/if}

<!-- Sidebar -->
{#if $is_authorized}
  <div class="fixed hidden md:block w-96 h-96 overflow-y-auto">
    <SidebarLayout />
  </div>
{/if}

<!-- Контент -->
<div class="md:ml-72">
  {@render children()}
</div>

<style>
  :global(body) {
    background-image: radial-gradient(#ff0000 0.65px, #2bff0000 0.65px);
    background-size: 13px 13px;
  }
</style>
