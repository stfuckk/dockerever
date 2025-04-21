<script>
  import { Select } from "flowbite-svelte";
  import { selected_node } from "$lib/stores/selected_node";
  import { onMount } from "svelte";

  export let nodes = [];

  let selectedIp = "";

  onMount(() => {
    const unsubscribe = selected_node.subscribe(node => {
      selectedIp = node?.ip ?? "";
    });
    return unsubscribe;
  });

  function handleChange() {
    const match = nodes.find(n => n.ip === selectedIp);
    if (match) {
      selected_node.set(match);
    }
  }
</script>

<Select
  class="mt-2 text-gray-900 dark:text-white bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 focus:ring-blue-500 focus:border-blue-500"
  placeholder="Выбор сервера"
  items={nodes.map(n => ({
    value: n.ip,
    name: `${n.hostname || 'Без имени'} (${n.ip})`
  }))}
  bind:value={selectedIp}
  on:change={handleChange}
/>
