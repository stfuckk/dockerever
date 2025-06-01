<script>
  import { onMount } from "svelte";
  import { Card } from "flowbite-svelte";
  import { getPrometheusRange } from "$lib/api/prometheus";

  export let title;
  export let query; // PromQL для container_fs_usage_bytes (в ГБ)
  export let instance;
  export let unit = ""; // не используется для disk
  export let metric_type = "";
  export let reloadSignal = 0;

  let error = "";

  // Для «disk» храним одну строку с байтами
  let diskRow = {
    device: "",
    usedBytes: null,
    totalBytes: null,
  };

  let usedDisplay = "";
  let totalDisplay = "";

  // Функция автоматически форматирует байты в Б, КБ, МБ или ГБ
  function formatValue(bytes) {
    if (bytes === null) return "—";
    if (bytes / 1024 / 1024 / 1024 >= 0.001) {
      return `${(bytes / 1024 / 1024 / 1024).toFixed(3)} ГБ`;
    } else if (bytes / 1024 / 1024 >= 0.001) {
      return `${(bytes / 1024 / 1024).toFixed(3)} МБ`;
    } else if (bytes / 1024 >= 0.001) {
      return `${(bytes / 1024).toFixed(3)} КБ`;
    } else {
      return `${bytes.toFixed(0)} Б`;
    }
  }

  // При смене diskRow сразу пересчитываем форматированные строки
  $: if (metric_type === "disk") {
    if (diskRow.usedBytes !== null && diskRow.totalBytes !== null) {
      usedDisplay = formatValue(diskRow.usedBytes);
      totalDisplay = formatValue(diskRow.totalBytes);
    }
  }

  // Загрузка значений для disk
  async function loadDiskValues() {
    error = "";

    try {
      // 1) Range-запрос за 5 минут для used (возвращает значение в ГБ)
      const now = Math.floor(Date.now() / 1000);
      const start = now - 300;
      const step = 60;
      const rr = await getPrometheusRange(query, instance, start, now, step);
      const series = rr.data?.result || [];
      if (series.length > 0) {
        const metric = series[0].metric;
        const values = series[0].values;
        const [_, lastValStr] = values[values.length - 1] || [null, null];
        const usedGB = lastValStr ? parseFloat(lastValStr) : 0;
        diskRow.device = metric.device || metric.mountpoint || "";
        // Переводим из ГБ в байты
        diskRow.usedBytes = usedGB * 1024 * 1024 * 1024;
      } else {
        diskRow.device = "";
        diskRow.usedBytes = 0;
      }

      // 2) Range-запрос за 5 минут для total (limit) — сразу байты
      const idLabel = series[0]?.metric.id || "";
      if (idLabel) {
        const limitQuery = `container_fs_limit_bytes{id=~"${idLabel}"}`;
        const lr = await getPrometheusRange(
          limitQuery,
          instance,
          start,
          now,
          step
        );
        const limSeries = lr.data?.result || [];
        if (limSeries.length > 0) {
          const limValues = limSeries[0].values;
          const [_, lastLimitStr] = limValues[limValues.length - 1] || [
            null,
            null,
          ];
          diskRow.totalBytes = lastLimitStr ? parseFloat(lastLimitStr) : 0;
        } else {
          diskRow.totalBytes = 0;
        }
      } else {
        diskRow.totalBytes = 0;
      }
    } catch (e) {
      console.error("ContainerTableBlock (disk) error:", e);
      error = "Ошибка при загрузке диска";
    }
  }

  // Для остальных метрик используем results
  let results = [];

  async function loadGeneric() {
    error = "";
    results = [];

    try {
      // Имитируем Instant через диапазон за 1 минуту
      const now = Math.floor(Date.now() / 1000);
      const start = now - 60;
      const step = 60;
      const resp = await getPrometheusRange(query, instance, start, now, step);
      results = resp.data?.result || [];
    } catch (e) {
      console.error("ContainerTableBlock (generic) error:", e);
      error = "Ошибка при загрузке данных";
    }
  }

  function load() {
    if (metric_type === "disk") {
      loadDiskValues();
    } else {
      loadGeneric();
    }
  }

  onMount(load);

  $: if (reloadSignal) {
    load();
  }

  $: if (instance && query) {
    load();
  }
</script>

<Card class="w-full max-w-none h-full flex flex-col">
  <h2 class="text-lg font-medium text-gray-800 dark:text-white mb-3">
    {title}
  </h2>
  <div class="flex-1 overflow-auto w-full">
    <table class="w-full text-sm text-left text-gray-700 dark:text-gray-300">
      <thead class="text-xs bg-gray-100 dark:bg-gray-700 dark:text-gray-200">
        <tr>
          {#if metric_type === "disk"}
            <th class="px-4 py-2">Устройство</th>
            <th class="px-4 py-2">Использовано / Всего</th>
          {:else if title === "Состояние сервисов"}
            <th class="px-4 py-2">Job</th>
            <th class="px-4 py-2">Up</th>
          {:else}
            {#if results.length > 0}
              {#each Object.keys(results[0].metric).filter((k) => k !== "__name__") as key}
                <th class="px-4 py-2">{key}</th>
              {/each}
            {/if}
            <th class="px-4 py-2">Value ({unit})</th>
          {/if}
        </tr>
      </thead>
      <tbody>
        {#if metric_type === "disk"}
          <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
            <td class="px-4 py-2">
              {#if error}
                <span class="text-red-500">Ошибка</span>
              {:else}
                {diskRow.device || "—"}
              {/if}
            </td>
            <td class="px-4 py-2">
              {#if error}
                <span class="text-red-500">Ошибка</span>
              {:else}
                {usedDisplay || "0 Б"} / {totalDisplay || "0 Б"}
              {/if}
            </td>
          </tr>
        {:else if title === "Состояние сервисов"}
          {#if error}
            <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
              <td class="px-4 py-2" colspan="2">
                <span class="text-red-500">Ошибка</span>
              </td>
            </tr>
          {:else if results.length === 0}
            <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
              <td class="px-4 py-2" colspan="2">
                <span class="text-gray-400">Нет данных</span>
              </td>
            </tr>
          {:else}
            {#each results as r}
              <tr
                class="bg-white border-b dark:bg-gray-800 dark:border-gray-700"
              >
                <td class="px-4 py-2">{r.job}</td>
                <td class="px-4 py-2">{r.up == 1 ? "Yes" : "No"}</td>
              </tr>
            {/each}
          {/if}
        {:else if error}
          <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
            <td class="px-4 py-2" colspan="100%">
              <span class="text-red-500">Ошибка</span>
            </td>
          </tr>
        {:else if results.length === 0}
          <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
            <td class="px-4 py-2" colspan="100%">
              <span class="text-gray-400">Нет данных</span>
            </td>
          </tr>
        {:else}
          {#each results as row}
            <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
              {#each Object.entries(row.metric).filter(([k]) => k !== "__name__") as [_, val]}
                <td class="px-4 py-2">{val}</td>
              {/each}
              <td class="px-4 py-2"
                >{parseFloat(row.value[1]).toFixed(3)} {unit}</td
              >
            </tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>
</Card>
