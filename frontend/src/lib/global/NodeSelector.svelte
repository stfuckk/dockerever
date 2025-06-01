<script>
  import { Select } from "flowbite-svelte";
  import { selected_node } from "$lib/stores/selected_node";

  export let nodes = [];

  // текущий hostname
  let selectedValue = "";
  // список опций для <Select>
  let items = [];

  // Как только придут nodes, один раз заполняем items и инициализируем selectedValue
  $: if (nodes.length > 0 && items.length === 0) {
    // собрать items из nodes
    items = nodes.map((n) => ({
      value: n.hostname,
      name: `${n.hostname} (${n.ip})`,
    }));

    // попробуем прочитать из localStorage
    let saved = null;
    try {
      saved = JSON.parse(localStorage.getItem("selected_node"));
    } catch {
      localStorage.removeItem("selected_node");
    }

    // ищем сначала по hostname, потом просто первую ноду
    const initialNode =
      (saved && nodes.find((n) => n.hostname === saved.hostname)) || nodes[0];

    selectedValue = initialNode.hostname;
    selected_node.set(initialNode);
    localStorage.setItem("selected_node", JSON.stringify(initialNode));
  }

  // При каждом изменении selectedValue — обновляем стор и localStorage
  $: if (selectedValue) {
    const node = nodes.find((n) => n.hostname === selectedValue);
    if (node) {
      selected_node.set(node);
      localStorage.setItem("selected_node", JSON.stringify(node));
    }
  }
</script>

{#if items.length > 0}
  <Select
    {items}
    bind:value={selectedValue}
    class="text-gray-900 dark:text-white bg-white dark:bg-gray-800
           border border-gray-300 dark:border-gray-600 focus:ring-blue-500
           focus:border-blue-500"
  />
{:else}
  <div class="text-gray-500 dark:text-gray-400 text-sm">
    Ожидание списка серверов…
  </div>
{/if}
