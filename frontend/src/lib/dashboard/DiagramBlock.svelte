<script>
  import { onMount, onDestroy } from "svelte";
  import { Card, Chart } from "flowbite-svelte";

  export let title;
  export let data = []; // data — это массив вида [[ metrics ]], где metrics.values = [[timestamp, value], …]
  export let unit = "";
  export let maxY = null;

  // Определяем текущую тему (светлая/тёмная)
  let isDark = localStorage.getItem("color-theme") === "dark";

  function updateTheme() {
    isDark = localStorage.getItem("color-theme") === "dark";
  }

  let observer;

  onMount(() => {
    // Слушаем изменение класса <html> (смена темы)
    observer = new MutationObserver((mutations) => {
      for (const m of mutations) {
        if (m.attributeName === "class") {
          updateTheme();
        }
      }
    });
    observer.observe(document.documentElement, { attributes: true });

    // Слушаем storage — на всякий случай
    window.addEventListener("storage", (e) => {
      if (e.key === "color-theme") updateTheme();
    });
  });

  onDestroy(() => {
    observer.disconnect();
    window.removeEventListener("storage", updateTheme);
  });

  const LABEL_COLOR = { light: "#000", dark: "#fff" };

  // Пересчитаем опции, когда меняются data, unit, maxY, isDark
  $: options = {
    chart: {
      type: "area",
      width: "100%",
      height: "100%",
      toolbar: { show: false },
      zoom: { enabled: false },
      fontFamily: "Inter, sans-serif",
      foreColor: isDark ? LABEL_COLOR.dark : LABEL_COLOR.light,
    },
    dataLabels: { enabled: false },
    stroke: { curve: "smooth", width: 2 },
    fill: {
      type: "gradient",
      gradient: {
        opacityFrom: 0.55,
        opacityTo: 0,
        shade: "#1C64F2",
        gradientToColors: ["#1C64F2"],
      },
    },
    tooltip: {
      x: {
        // форматируем подсказку «X» как HH:MM
        formatter: (val) => {
          const d = new Date(val);
          return d.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          });
        },
      },
      y: { formatter: (v) => `${v?.toFixed(3) ?? v} ${unit}` },
    },
    xaxis: {
      type: "datetime",
      labels: {
        rotate: -45,
        style: { colors: [isDark ? LABEL_COLOR.dark : LABEL_COLOR.light] },
        hideOverlappingLabels: true,
        datetimeUTC: false,
        format: "HH:mm", // задаём формат «ЧЧ:мм»
      },
      // автоматически выбираем разумное количество делений
      tickAmount: 6,
    },
    yaxis: {
      title: { text: unit },
      labels: {
        formatter: (v) => v.toFixed(3),
        style: { colors: [isDark ? LABEL_COLOR.dark : LABEL_COLOR.light] },
      },
      ...(maxY != null ? { max: maxY } : {}),
      min: 0,
    },
    series: [
      {
        name: title,
        // здесь мы передаём не просто «значения», а [{ x: timestamp_in_ms, y: value }, …]
        data:
          data[0]?.values?.map(([ts, v]) => ({
            x: ts * 1000,
            y: parseFloat(v),
          })) || [],
      },
    ],
  };
</script>

<Card class="w-full max-w-none h-full flex flex-col">
  <h2 class="text-lg font-medium text-gray-800 dark:text-white mb-2">
    {title}
  </h2>
  <div class="flex-1 w-full">
    <Chart {options} />
  </div>
</Card>
