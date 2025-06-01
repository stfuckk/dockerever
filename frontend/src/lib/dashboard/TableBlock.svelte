<script>
  import { onMount } from "svelte";
  import { Card } from "flowbite-svelte";
  import { getPrometheusQuery } from "$lib/api/prometheus";

  export let title;
  export let query;
  export let instance;
  export let unit = "";
  export let metric_type = "";

  let loading = true;
  let error = "";
  let results = [];

  async function load() {
    loading = true;
    error = "";
    results = [];

    try {
      if (metric_type === "disk") {
        // 1) получить used
        const resp = await getPrometheusQuery(query, instance);
        const usedRows = resp.data?.result || [];

        // 2) для каждого mountpoint — взять полный размер
        const rows = [];
        for (const row of usedRows) {
          const mp = row.metric.mountpoint;
          const used = parseFloat(row.value[1]);
          // полный размер
          const totResp = await getPrometheusQuery(
            `node_filesystem_size_bytes{instance="${instance}",mountpoint="${mp}"}`
          );
          const totRow = totResp.data?.result?.[0];
          const total = totRow ? parseFloat(totRow.value[1]) : 0;
          rows.push({ mountpoint: mp, used, total });
        }
        results = rows;
      } else if (title === "Состояние сервисов") {
        // Состояние сервисов — два запроса в ряд
        const jobs = ["node_exporter", "cadvisor"];
        const rows = [];
        for (const job of jobs) {
          const resp = await getPrometheusQuery(
            `up{instance="${instance}",job="${job}"}`
          );
          const v = resp.data?.result?.[0]?.value?.[1] ?? 0;
          rows.push({ job, instance, up: v });
        }
        results = rows;
      } else {
        // Generic: просто берём metrics[result]
        const resp = await getPrometheusQuery(query, instance);
        results = resp.data?.result || [];
      }
    } catch (e) {
      console.error(e);
      error = "Ошибка при загрузке данных";
    }

    loading = false;
  }

  onMount(load);
  $: instance, load();

  function formatDisk(used, total) {
    const u = (used / 1024 / 1024 / 1024).toFixed(3);
    const t = (total / 1024 / 1024 / 1024).toFixed(3);
    return `${u} / ${t} ГБ`;
  }

  function formatGeneric(val) {
    return `${parseFloat(val).toFixed(3)} ${unit}`;
  }

  function formatService(v) {
    return v == 1 ? "Yes" : "No";
  }
</script>

<Card class="w-full max-w-none h-full flex flex-col">
  <h2 class="text-lg font-medium text-gray-800 dark:text-white mb-3">
    {title}
  </h2>
  <div class="flex-1 overflow-auto w-full">
    {#if loading}
      <div class="text-gray-500 dark:text-gray-400">Загрузка...</div>
    {:else if error}
      <div class="text-red-500">{error}</div>
    {:else if results.length === 0}
      <div class="text-gray-400">Нет данных</div>
    {:else}
      <div class="overflow-auto">
        <table
          class="w-full text-sm text-left text-gray-700 dark:text-gray-300"
        >
          <thead
            class="text-xs bg-gray-100 dark:bg-gray-700 dark:text-gray-200"
          >
            <tr>
              {#if metric_type === "disk"}
                <th class="px-4 py-2">mountpoint</th>
                <th class="px-4 py-2">Использовано / Всего</th>
              {:else if title === "Состояние сервисов"}
                <th class="px-4 py-2">job</th>
                <th class="px-4 py-2">status</th>
              {:else}
                {#each Object.keys(results[0].metric).filter((k) => k !== "__name__") as key}
                  <th class="px-4 py-2">{key}</th>
                {/each}
                <th class="px-4 py-2">Value</th>
              {/if}
            </tr>
          </thead>
          <tbody>
            {#if metric_type === "disk"}
              {#each results as row}
                <tr
                  class="bg-white border-b dark:bg-gray-800 dark:border-gray-700"
                >
                  <td class="px-4 py-2">{row.mountpoint}</td>
                  <td class="px-4 py-2">{formatDisk(row.used, row.total)}</td>
                </tr>
              {/each}
            {:else if title === "Состояние сервисов"}
              {#each results as r}
                <tr
                  class="bg-white border-b dark:bg-gray-800 dark:border-gray-700"
                >
                  <td class="px-4 py-2">{r.job}</td>
                  <td class="px-4 py-2">{formatService(r.up)}</td>
                </tr>
              {/each}
            {:else}
              {#each results as row}
                <tr
                  class="bg-white border-b dark:bg-gray-800 dark:border-gray-700"
                >
                  {#each Object.entries(row.metric).filter(([k]) => k !== "__name__") as [_, val]}
                    <td class="px-4 py-2">{val}</td>
                  {/each}
                  <td class="px-4 py-2">{formatGeneric(row.value[1])}</td>
                </tr>
              {/each}
            {/if}
          </tbody>
        </table>
      </div>
    {/if}
  </div></Card
>
