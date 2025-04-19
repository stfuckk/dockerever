<script>
  import "../app.css";
  import NavigationBar from "$lib/global/NavigationBar.svelte";
  import SidebarLayout from "$lib/global/SidebarLayout.svelte"; // импорт сайдбара
  import { isAuthorized as authCheck } from "$lib/api/auth";
  import { is_authorized, user } from "$lib/stores/authStore";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import { get } from "svelte/store";
  import MobileNav from "$lib/global/MobileNav.svelte";
  import NodeSelector from "$lib/global/NodeSelector.svelte";

  let { children } = $props();
  let selectedNode = $state("");
  let nodes = $state(["172.18.6.133:9100", "172.18.6.134:9100"]);
  onMount(async () => {
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

  const currentUser = get(user);
</script>

<NavigationBar />

{#if $is_authorized}
  <div class="hidden md:block">
    <SidebarLayout />
  </div>

  <div class="md:hidden">
    <NodeSelector {nodes} bind:selectedNode />
    <MobileNav />
  </div>
{/if}
{@render children()}
