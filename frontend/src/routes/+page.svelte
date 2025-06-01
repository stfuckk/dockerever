<script>
  import { onMount } from "svelte";
  import { get } from "svelte/store";
  import { selected_node } from "$lib/stores/selected_node";
  import { getDashboardByTitle } from "$lib/api/dashboards";
  import { getPrometheusRange, getPrometheusQuery } from "$lib/api/prometheus";
  import DiagramBlock from "$lib/dashboard/DiagramBlock.svelte";
  import TableBlock from "$lib/dashboard/TableBlock.svelte";
  import { Label, Select, Spinner } from "flowbite-svelte";

  // Список диапазонов
  const RANGE_OPTIONS = [
    { value: "5m", label: "5 мин", seconds: 5 * 60 },
    { value: "3h", label: "3 ч", seconds: 3 * 3600 },
    { value: "6h", label: "6 ч", seconds: 6 * 3600 },
    { value: "24h", label: "24 ч", seconds: 24 * 3600 },
  ];

  // Текущий выбранный value и объект
  let selectedValue = RANGE_OPTIONS[0].value;
  let selectedRange = RANGE_OPTIONS[0];

  // При смене select
  function onChangeRange(v) {
    selectedValue = v;
    selectedRange = RANGE_OPTIONS.find((o) => o.value === v);
    loadingDashboard = true;
    loadDashboard();
  }

  let dashboard = null;
  let metrics = {};
  let totalMemoryGB = null;
  let error = "";
  let loadingDashboard = true;
  const REFRESH_INTERVAL = 10000;

  async function loadDashboard() {
    const node = get(selected_node);
    if (!node?.hostname) return;

    try {
      if (!dashboard) {
        dashboard = await getDashboardByTitle("Основной серверный мониторинг");
      }
      if (totalMemoryGB === null) {
        const resp = await getPrometheusQuery(
          "node_memory_MemTotal_bytes",
          node.hostname
        );
        const rawBytes = resp.data?.result?.[0]?.value?.[1] ?? 0;
        totalMemoryGB = rawBytes / 1024 / 1024 / 1024;
      }

      const now = Math.floor(Date.now() / 1000);
      const start = now - selectedRange.seconds;
      const step = Math.max(10, Math.floor(selectedRange.seconds / 100));

      const newM = {};
      for (const blk of dashboard.blocks) {
        if (blk.type === "diagram") {
          const res = await getPrometheusRange(
            blk.prometheus_query,
            node.hostname,
            start,
            now,
            step
          );
          newM[blk.id] = res.data?.result || [];
        }
      }

      metrics = newM;
      error = "";
    } catch (e) {
      console.error(e);
      error = "Ошибка при загрузке метрик";
    } finally {
      loadingDashboard = false;
    }
  }

  onMount(() => {
    try {
      const saved = JSON.parse(localStorage.getItem("selected_node"));
      if (saved?.hostname) selected_node.set(saved);
    } catch {}

    const unsub = selected_node.subscribe((node) => {
      if (node?.hostname) {
        loadingDashboard = true;
        loadDashboard();
      }
    });

    loadDashboard();
    const timer = setInterval(loadDashboard, REFRESH_INTERVAL);

    return () => {
      unsub();
      clearInterval(timer);
    };
  });
</script>

{#if loadingDashboard}
  <div class="text-center mt-20 text-gray-600 dark:text-gray-300">
    Загрузка дашборда…
    <Spinner />
  </div>
{:else}
  <div class="p-4 space-y-4 w-full">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">
        Серверный мониторинг: {$selected_node.hostname}
      </h1>

      <Label>
        Период
        <Select
          class="mt-1"
          items={RANGE_OPTIONS.map((o) => ({ value: o.value, name: o.label }))}
          bind:value={selectedValue}
          on:change={() => onChangeRange(selectedValue)}
        />
      </Label>
    </div>

    {#if error}
      <div class="text-red-500">{error}</div>
    {/if}

    {#each dashboard.blocks as blk}
      <div class="w-full h-[32rem] flex flex-col">
        {#if blk.type === "diagram"}
          <DiagramBlock
            class="w-full h-full"
            title={blk.title}
            data={metrics[blk.id] || []}
            unit={blk.unit}
            maxY={blk.metric_type === "cpu"
              ? 100
              : blk.metric_type === "memory"
                ? totalMemoryGB
                : blk.metric_type === "network"
                  ? 100
                  : null}
          />
        {:else}
          <TableBlock
            class="w-full h-full overflow-auto"
            title={blk.title}
            query={blk.prometheus_query}
            instance={$selected_node.hostname}
            unit={blk.unit}
            metric_type={blk.metric_type}
          />
        {/if}
      </div>
    {/each}
  </div>
{/if}
