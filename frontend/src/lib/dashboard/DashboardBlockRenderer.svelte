<script>
  import DashboardDiagram from "./DashboardDiagram.svelte";
  import DashboardTable from "./DashboardTable.svelte";
  export let block;
</script>

<div class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
  <h3 class="text-lg font-semibold mb-2 dark:text-white">{block.title}</h3>

  {#if block.type === "diagram"}
    <DashboardDiagram query={block.prometheus_query} unit={block.unit} />
  {:else if block.type === "table"}
    <DashboardTable query={block.prometheus_query} unit={block.unit} />
  {:else}
    <p>Неизвестный тип блока: {block.type}</p>
  {/if}
</div>
