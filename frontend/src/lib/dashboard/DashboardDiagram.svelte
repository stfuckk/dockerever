<script>
  import { onMount, onDestroy } from "svelte";
  import { Card, Chart } from "flowbite-svelte";
  import { selected_node } from "$lib/stores/selected_node";
  import { get } from "svelte/store";
  import { authFetch } from "$lib/api/auth";

  export let query;
  export let unit;

  let chartOptions = {};
  let series = [{ name: unit || "Значение", data: [], color: "#1A56DB" }];
  let categories = [];
  let errorMessage = "";
  let loading = true;
  let interval;
  let lastHostname = null;

  $: $selected_node, query, fetchMetrics();

  async function fetchMetrics() {
    try {
      if (!$selected_node) throw new Error("Не выбран сервер");

      // Показываем загрузку ТОЛЬКО при смене сервера
      if (lastHostname !== $selected_node) {
        loading = true;
        lastHostname = $selected_node;
      }

      const end = Math.floor(Date.now() / 1000);
      const start = end - 60 * 5;
      const step = 30;

      const res = await authFetch(
        `/api/v1/prometheus/range?query=${encodeURIComponent(query)}&instance=${encodeURIComponent($selected_node)}&start=${start}&end=${end}&step=${step}`
      );
      const result = await res.json();

      if (!result?.data?.result?.length) {
        errorMessage = "Нет данных";
        return;
      }

      const values = result.data.result[0].values;

      series[0].data = values.map(v => parseFloat(v[1]).toFixed(2));
      categories = values.map(v => {
        const d = new Date(v[0] * 1000);
        return `${d.getHours()}:${String(d.getMinutes()).padStart(2, "0")}`;
      });

      chartOptions = {
        chart: {
          height: 350,
          type: "line",
          toolbar: { show: false },
          fontFamily: "Inter, sans-serif"
        },
        stroke: { width: 4, curve: "smooth" },
        grid: {
          show: true,
          strokeDashArray: 4,
          padding: { left: 2, right: 2, top: 0 }
        },
        xaxis: {
          categories,
          labels: {
            style: {
              fontFamily: "Inter, sans-serif",
              cssClass: "text-xs font-normal fill-gray-500 dark:fill-gray-400"
            }
          }
        },
        yaxis: {
          labels: {
            style: {
              fontFamily: "Inter, sans-serif",
              cssClass: "text-xs font-normal fill-gray-500 dark:fill-gray-400"
            }
          }
        },
        series
      };

      errorMessage = "";
    } catch (err) {
      errorMessage = err.message || "Ошибка загрузки";
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    fetchMetrics(); // первая загрузка
    interval = setInterval(fetchMetrics, 5000); // обновление по таймеру
  });

  onDestroy(() => clearInterval(interval));
</script>

<Card class="dark:bg-gray-800">
  {#if loading}
    <p class="text-sm text-gray-400">Загрузка...</p>
  {:else if errorMessage}
    <p class="text-sm text-red-500 dark:text-red-400">Ошибка: {errorMessage}</p>
  {:else if chartOptions?.chart}
    <Chart options={chartOptions} />
  {:else}
    <p class="text-sm text-gray-400">Нет данных для отображения</p>
  {/if}
</Card>
