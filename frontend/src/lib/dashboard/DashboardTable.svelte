<script>
  import { selected_node } from "$lib/stores/selected_node";
  import { get } from "svelte/store";
  import { onMount } from "svelte";
  import { authFetch } from "$lib/api/auth";

  export let query;
  export let unit;

  let rows = [];

  onMount(async () => {
    const node = get(selected_node);
    const instance = node?.hostname;

    const url = `/api/v1/prometheus?query=${encodeURIComponent(query)}${instance ? `&instance=${encodeURIComponent(instance)}` : ""}`;
    const res = await authFetch(url);
    const result = await res.json();
    rows = result.data.result;
  });

  function formatBytes(bytes) {
    const sizes = ["B", "KB", "MB", "GB", "TB"];
    if (bytes === "0") return "0 B";
    const i = Math.floor(Math.log(parseFloat(bytes)) / Math.log(1024));
    return `${(parseFloat(bytes) / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  }
</script>

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
