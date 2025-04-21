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

  let { children } = $props();
  let nodes = $state([]);

  onMount(async () => {
    const res = await authFetch("/api/v1/nodes");
    nodes = await res.json();

    // Загрузка из localStorage или первый из списка
    const saved = localStorage.getItem("selected_node");
    const parsed = saved ? JSON.parse(saved) : nodes[0];
    selected_node.set(parsed);

    const currentUser = await authCheck();

    if (!currentUser) {
      is_authorized.set(false);
      goto("/login");
      return;
    }

    if (currentUser.must_change_password) {
      goto("/login?reason=must_change_password");
      return;
    }

    user.set(currentUser);
    is_authorized.set(true);
  });

  // Автосохранение выбранного узла
  $effect(() => {
    const node = get(selected_node);
    if (node) {
      localStorage.setItem("selected_node", JSON.stringify(node));
    }
  });
</script>

<NavigationBar />

{#if $is_authorized}
  <!-- Sidebar -->
  <div class="hidden md:block fixed z-9998 overflow-y-auto w-96 mt-8 h-96">
    <SidebarLayout />
  </div>

  <!-- NodeSelector desktop -->
  <div class="hidden md:block fixed z-9999 w-auto mt-4 pl-4">
    <NodeSelector {nodes} />
  </div>

  <!-- NodeSelector mobile -->
  <div class="md:hidden fixed z-9999 w-[95%] mt-4 top-14 pl-4">
    <NodeSelector {nodes} />
  </div>

  <div class="md:hidden">
    <MobileNav />
  </div>
{/if}

<!-- Контент -->
{#if $is_authorized}
  <div class="hidden md:block ml-96 w-auto">
    {@render children()}
  </div>
{:else}
  <div class="hidden md:block w-auto">
    {@render children()}
  </div>
{/if}

<div class="md:hidden pl-2">
  {@render children()}
</div>
