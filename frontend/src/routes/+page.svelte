<script>
  import { onMount } from "svelte";
  import { authFetch } from "$lib/api/auth";
  import DashboardBlockRenderer from "$lib/dashboard/DashboardBlockRenderer.svelte";
  import { Spinner } from "flowbite-svelte";
  import { selected_node } from "$lib/stores/selected_node";

  let dashboard = null;

  $: $selected_node; // отслеживаем изменения

  onMount(async () => {
    try {
      const res = await authFetch("/api/v1/dashboards");
      const dashboards = await res.json();
      dashboard = dashboards.find((d) => d.system);
    } catch (err) {
      console.error("Ошибка загрузки дашбордов:", err);
    }
  });
</script>

<div class="mt-32 mb-24 px-4">
  {#if dashboard && $selected_node}
    <h1 class="text-2xl font-bold mb-6 dark:text-white">{dashboard.title}</h1>
    <div
      class="grid gap-6 grid-cols-1 md:grid-cols-1 xl:grid-cols-2 2xl:grid-cols-3"
    >
      {#each dashboard.blocks as block (block.id + "-" + $selected_node?.ip)}
        <DashboardBlockRenderer {block} />
      {/each}
    </div>
  {:else}
    <Spinner />
  {/if}
</div>
