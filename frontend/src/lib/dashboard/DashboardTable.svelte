<script>
  import { selected_node } from "$lib/stores/selected_node";
  import { get } from "svelte/store";
  import { onMount } from "svelte";
  import { authFetch } from "$lib/api/auth";

  export let query;
  export let unit;

  let rows = [];
  let loading = true;
  let errorMessage = "";
  let lastHostname = null;

  $: $selected_node, query, fetchTable();

  async function fetchTable() {
    try {
      if (!$selected_node) throw new Error("Не выбран сервер");

      if (lastHostname !== $selected_node) {
        loading = true;
        lastHostname = $selected_node;
      }

      const instance = $selected_node;
      const url = `/api/v1/prometheus?query=${encodeURIComponent(query)}&instance=${encodeURIComponent(instance)}`;
      const res = await authFetch(url);
      const result = await res.json();

      rows = result.data.result;
      errorMessage = "";
    } catch (err) {
      errorMessage = err.message || "Ошибка загрузки";
    } finally {
      loading = false;
    }
  }

  function formatBytes(bytes) {
    const sizes = ["B", "KB", "MB", "GB", "TB"];
    if (bytes === "0") return "0 B";
    const i = Math.floor(Math.log(parseFloat(bytes)) / Math.log(1024));
    return `${(parseFloat(bytes) / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  }
</script>

{#if loading}
  <p class="text-sm text-gray-400">Загрузка...</p>
{:else if errorMessage}
  <p class="text-sm text-red-500 dark:text-red-400">Ошибка: {errorMessage}</p>
{:else}
<table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
  <thead
    class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400"
  >
    <tr>
      <th class="px-4 py-2">Данные</th>
      <th class="px-4 py-2">Значение {unit && `(${unit})`}</th>
    </tr>
  </thead>
  <tbody>
    {#each rows as row}
      <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
        <td class="px-4 py-2">
          {row.metric.mountpoint ||
            row.metric.instance ||
            Object.values(row.metric)[0]}
        </td><td class="px-4 py-2">
          {unit === "используется из общего" ? formatBytes(row.value[1]) : row.value[1]}
        </td>
      </tr>
    {/each}
  </tbody>
</table>
{/if}