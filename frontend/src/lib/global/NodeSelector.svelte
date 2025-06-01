<script>
  import { Select } from "flowbite-svelte";
  import { selected_node } from "$lib/stores/selected_node";
  import { get } from "svelte/store";

  // Принимаем prop `nodes` (массив объектов { hostname, ip, ... })
  export let nodes = [];

  // Текущий выбранный hostname
  let selectedValue = "";

  // На каждый рендер (или когда меняется `nodes`) пересчитываем список опций
  $: items = Array.isArray(nodes)
    ? nodes.map((n) => ({
        value: n.hostname,
        name: `${n.hostname} (${n.ip})`,
      }))
    : [];

  // Как только `nodes` превращается в непустой массив, проверяем, валиден ли текущий `selectedValue`.
  // Если его нет, либо он не совпадает ни с одним из `nodes.hostname`,
  // берём либо из localStorage, либо просто первый элемент `nodes[0]`.
  $: if (Array.isArray(nodes) && nodes.length > 0) {
    const exists = nodes.find((n) => n.hostname === selectedValue);
    if (!exists) {
      let saved = null;
      try {
        saved = JSON.parse(localStorage.getItem("selected_node"));
      } catch {
        localStorage.removeItem("selected_node");
      }

      const initialNode =
        (saved && nodes.find((n) => n.hostname === saved.hostname)) || nodes[0];

      // Устанавливаем `selectedValue` и стор
      selectedValue = initialNode.hostname;
      selected_node.set(initialNode);
      localStorage.setItem("selected_node", JSON.stringify(initialNode));
    }
  }

  // Каждый раз, когда меняется selectedValue, сохраняем в стор и localStorage
  $: if (selectedValue) {
    const node = Array.isArray(nodes)
      ? nodes.find((n) => n.hostname === selectedValue)
      : null;
    if (node) {
      selected_node.set(node);
      localStorage.setItem("selected_node", JSON.stringify(node));
    }
  }
</script>

{#if localStorage.getItem("selected_node") || nodes.length > 0}
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
