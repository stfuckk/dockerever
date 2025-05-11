<script>
  import { Select } from "flowbite-svelte";
  import { selected_node } from "$lib/stores/selected_node";
  import { get } from "svelte/store";

  export let nodes = [];

  let current = get(selected_node) || nodes[0];
  selected_node.set(current);

  function select(node) {
    selected_node.set(node);
    localStorage.setItem("selected_node", JSON.stringify(node));
    current = node;
  }
</script>

<Select
  class="text-gray-900 dark:text-white bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 focus:ring-blue-500 focus:border-blue-500"
  placeholder="Выбор сервера"
  items={nodes.map((n) => ({
    value: n.hostname,
    name: `${n.hostname || "Без имени"} (${n.ip})`,
  }))}
  bind:value={current}
  on:change={() => select(current)}
/>
