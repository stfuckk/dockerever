<script>
  import { onMount, onDestroy } from "svelte";
  import { page } from "$app/stores";
  import { get } from "svelte/store";
  import { selected_node } from "$lib/stores/selected_node";

  import {
    getDashboardByTitle,
    createDashboardBlock,
    updateDashboardBlock,
    deleteDashboardBlock,
  } from "$lib/api/dashboards";
  import { getContainers } from "$lib/api/docker";
  import { getPrometheusRange, getPrometheusQuery } from "$lib/api/prometheus";

  import DiagramBlock from "$lib/dashboard/DiagramBlock.svelte";
  import ContainerTableBlock from "$lib/dashboard/ContainerTableBlock.svelte";

  import { Label, Select, Modal, Input, Button } from "flowbite-svelte";
  import {
    CogOutline,
    TrashBinOutline,
    PlusOutline,
  } from "flowbite-svelte-icons";

  // ID дашборда из URL
  let dashboardTitle = "";
  $: dashboardTitle = $page.params.id;

  let dashboard = null;
  let blocks = [];
  let metricsData = {}; // { [blockId]: [] }
  let maxYMap = {}; // { [blockId]: number }
  let containersList = [];
  let containersMap = {};
  let loadError = "";
  let loading = true;

  // Диапазоны в секундах
  let selectedRange = 300;
  const TIME_RANGES = [
    { value: 300, label: "5 мин" },
    { value: 3600, label: "1 ч" },
    { value: 10800, label: "3 ч" },
    { value: 21600, label: "6 ч" },
    { value: 86400, label: "24 ч" },
  ];

  // Сигнал для табличных блоков
  let reloadCounter = 0;

  // Drag’n’Drop
  let draggedIndex = null;

  // ID таймера
  let intervalId = null;

  // ===== Сохранение/восстановление порядка блоков =====
  function loadSavedOrder(list) {
    try {
      const key = `dashboard-order-${dashboard.id}`;
      const saved = JSON.parse(localStorage.getItem(key));
      if (Array.isArray(saved)) {
        const byId = Object.fromEntries(list.map((b) => [b.id, b]));
        const ordered = saved.map((id) => byId[id]).filter(Boolean);
        const rest = list.filter((b) => !saved.includes(b.id));
        return [...ordered, ...rest];
      }
    } catch {}
    return list;
  }
  function saveOrder() {
    try {
      const key = `dashboard-order-${dashboard.id}`;
      const ids = blocks.map((b) => b.id);
      localStorage.setItem(key, JSON.stringify(ids));
    } catch {}
  }

  // ===== Загрузка контейнеров (с учётом фильтра) =====
  // теперь getContainers принимает строку фильтра — containerSearch.trim()
  async function loadContainers() {
    try {
      const res = await getContainers(containerSearch.trim());
      containersList = res.containers || [];
      containersMap = {};
      for (const c of containersList) {
        containersMap[c.id] = c.name;
      }
    } catch (e) {
      console.error("Ошибка при загрузке контейнеров:", e);
      containersList = [];
      containersMap = {};
    }
  }

  // ===== Загрузка структуры дашборда =====
  async function loadDashboardStructure() {
    loading = true;
    loadError = "";
    metricsData = {};
    maxYMap = {};

    if (!dashboardTitle) {
      loadError = "Не указан заголовок дашборда";
      loading = false;
      return;
    }
    try {
      dashboard = await getDashboardByTitle(dashboardTitle);
      let fetched = dashboard.blocks || [];

      // Загрузим контейнеры для блоков, чтобы заполнить containersMap
      for (const b of fetched) {
        if (b.container_id && !containersMap[b.container_id]) {
          await loadContainers();
        }
      }

      // Рассчитываем maxY для диаграмм (cpu, network, memory)
      await Promise.all(
        fetched.map(async (b) => {
          if (b.type === "diagram") {
            if (b.metric_type === "cpu") {
              maxYMap[b.id] = 100;
            } else if (
              b.metric_type === "network_in" ||
              b.metric_type === "network_out"
            ) {
              maxYMap[b.id] = 100;
            } else if (b.metric_type === "memory") {
              try {
                const node = get(selected_node);
                const instance = node?.hostname || node?.ip || "";
                const now = Math.floor(Date.now() / 1000);
                const start = now - selectedRange;
                const step = Math.max(Math.floor(selectedRange / 40), 1);
                const resp = await getPrometheusRange(
                  "node_memory_MemTotal_bytes",
                  instance,
                  start,
                  now,
                  step
                );
                const vals = resp.data?.result?.[0]?.values || [];
                const last = vals.length
                  ? parseFloat(vals[vals.length - 1][1])
                  : null;
                if (last !== null) {
                  maxYMap[b.id] = +(last / 1024 / 1024 / 1024).toFixed(3);
                } else {
                  maxYMap[b.id] = null;
                }
              } catch {
                maxYMap[b.id] = null;
              }
            }
          }
        })
      );

      blocks = loadSavedOrder(fetched);
    } catch (e) {
      console.error("Ошибка при загрузке дашборда:", e);
      loadError = "Не удалось загрузить дашборд";
      blocks = [];
    } finally {
      loading = false;
    }
  }

  // ===== Обновление метрик =====
  async function refreshMetricsData() {
    if (!dashboard) return;

    const node = get(selected_node);
    const instance = node?.hostname || node?.ip || "";
    const now = Math.floor(Date.now() / 1000);
    const start = now - selectedRange;
    const step = Math.max(Math.floor(selectedRange / 40), 1);

    // Диаграммы
    const diagramBlocks = blocks.filter((b) => b.type === "diagram");
    const newMetrics = { ...metricsData };
    await Promise.all(
      diagramBlocks.map(async (b) => {
        try {
          const resp = await getPrometheusRange(
            b.prometheus_query,
            instance,
            start,
            now,
            step
          );
          newMetrics[b.id] = resp.data?.result || [];
        } catch (e) {
          console.error(`Ошибка для блока ${b.id}:`, e);
          newMetrics[b.id] = [];
        }
      })
    );
    metricsData = newMetrics;

    // Табличные блоки — просто увеличиваем счётчик
    reloadCounter += 1;
  }

  // ===== Drag’n’Drop =====
  function onDragStart(e, idx) {
    draggedIndex = idx;
    e.dataTransfer.setData("text/plain", idx);
    e.dataTransfer.effectAllowed = "move";
  }
  function onDragOver(e) {
    e.preventDefault();
  }
  function onDrop(e, targetIdx) {
    e.preventDefault();
    const from = draggedIndex;
    const to = targetIdx;
    if (from != null && to != null && from !== to) {
      const swapped = [...blocks];
      [swapped[from], swapped[to]] = [swapped[to], swapped[from]];
      blocks = swapped;
      saveOrder();
    }
    draggedIndex = null;
  }

  // ===== Lifecycle =====
  onMount(async () => {
    // Изначально: загрузка пустого списка контейнеров + структура + первые метрики
    await loadContainers(); // загрузим все контейнеры (без фильтра)
    await loadDashboardStructure();
    await refreshMetricsData();
    intervalId = setInterval(refreshMetricsData, 5000);

    // При смене выбранного узла — перезагрузить дашборд
    const unsub = selected_node.subscribe((node) => {
      if (node?.hostname && dashboard) {
        loadDashboardStructure().then(refreshMetricsData);
      }
    });

    onDestroy(() => {
      clearInterval(intervalId);
      unsub();
    });
  });

  // ===== Реактивность =====
  // При смене диапазона — сразу запрос новых данных
  $: if (selectedRange) {
    refreshMetricsData();
  }

  // ===== Создание / редактирование / удаление блоков =====
  let showAddModal = false;
  let formContainerId = "";
  let formMetricType = "";
  let formTitle = "";
  let formError = "";
  let containerSearch = ""; // Строка поиска внутри модалки

  function openAddModal() {
    formContainerId = "";
    formMetricType = "";
    formTitle = "";
    formError = "";
    containerSearch = ""; // очистим строку поиска
    loadContainers(); // загрузим полный список контейнеров
    showAddModal = true;
  }

  async function submitAdd() {
    formError = "";
    if (!formContainerId || !formMetricType || !formTitle.trim()) {
      formError = "Заполните все поля";
      return;
    }
    const METRICS = [
      { value: "cpu", type: "diagram", unit: "%" },
      { value: "memory", type: "diagram", unit: "ГБ" },
      { value: "network_in", type: "diagram", unit: "МБ/с" },
      { value: "network_out", type: "diagram", unit: "МБ/с" },
      { value: "disk", type: "table", unit: "ГБ" },
    ];
    const metric = METRICS.find((m) => m.value === formMetricType);
    const payload = {
      title: formTitle.trim(),
      type: metric.type,
      unit: metric.unit,
      container_id: formContainerId,
      metric_type: formMetricType,
      prometheus_query: "",
    };
    try {
      const newBlock = await createDashboardBlock(dashboard.id, payload);
      blocks = [...blocks, newBlock];
      saveOrder();

      if (newBlock.type === "diagram") {
        if (newBlock.metric_type === "cpu") maxYMap[newBlock.id] = 100;
        if (
          newBlock.metric_type === "network_in" ||
          newBlock.metric_type === "network_out"
        )
          maxYMap[newBlock.id] = 100;
        if (newBlock.metric_type === "memory") {
          try {
            const node = get(selected_node);
            const instance = node?.hostname || node?.ip || "";
            const now = Math.floor(Date.now() / 1000);
            const start = now - selectedRange;
            const step = Math.max(Math.floor(selectedRange / 40), 1);
            const resp = await getPrometheusRange(
              `container_spec_memory_limit_bytes{id=~"/docker/${newBlock.container_id}"}`,
              instance,
              start,
              now,
              step
            );
            const val = resp.data?.result?.[0]?.value?.[1] ?? null;
            maxYMap[newBlock.id] =
              val !== null
                ? +(parseFloat(val) / 1024 / 1024 / 1024).toFixed(3)
                : null;
          } catch {
            maxYMap[newBlock.id] = null;
          }
        }
        await refreshMetricsData();
      }
      showAddModal = false;
    } catch (e) {
      console.error("Ошибка создания блока:", e);
      formError = "Не удалось создать";
    }
  }

  let showEditModal = false;
  let editBlockData = null;

  function openEditModal(block) {
    editBlockData = block;
    formContainerId = block.container_id || "";
    formMetricType = block.metric_type || "";
    formTitle = block.title || "";
    formError = "";
    containerSearch = "";
    loadContainers(); // чтобы загрузить (и обновить) список контейнеров при редактировании
    showEditModal = true;
  }

  async function submitEdit() {
    formError = "";
    if (!formContainerId || !formMetricType || !formTitle.trim()) {
      formError = "Заполните все поля";
      return;
    }
    const METRICS = [
      { value: "cpu", type: "diagram", unit: "%" },
      { value: "memory", type: "diagram", unit: "ГБ" },
      { value: "network_in", type: "diagram", unit: "МБ/с" },
      { value: "network_out", type: "diagram", unit: "МБ/с" },
      { value: "disk", type: "table", unit: "ГБ" },
    ];
    const metric = METRICS.find((m) => m.value === formMetricType);
    const payload = {
      title: formTitle.trim(),
      type: metric.type,
      unit: metric.unit,
      container_id: formContainerId,
      metric_type: formMetricType,
      prometheus_query: "",
    };
    try {
      const updated = await updateDashboardBlock(editBlockData.id, payload);
      blocks = blocks.map((b) => (b.id === updated.id ? updated : b));
      saveOrder();

      if (updated.type === "diagram") {
        if (updated.metric_type === "cpu") maxYMap[updated.id] = 100;
        if (
          updated.metric_type === "network_in" ||
          updated.metric_type === "network_out"
        )
          maxYMap[updated.id] = 100;
        if (updated.metric_type === "memory") {
          try {
            const node = get(selected_node);
            const instance = node?.hostname || node?.ip || "";
            const now = Math.floor(Date.now() / 1000);
            const start = now - selectedRange;
            const step = Math.max(Math.floor(selectedRange / 40), 1);
            const resp = await getPrometheusRange(
              `container_spec_memory_limit_bytes{id=~"/docker/${updated.container_id}"}`,
              instance,
              start,
              now,
              step
            );
            const val = resp.data?.result?.[0]?.value?.[1] ?? null;
            maxYMap[updated.id] =
              val !== null
                ? +(parseFloat(val) / 1024 / 1024 / 1024).toFixed(3)
                : null;
          } catch {
            maxYMap[updated.id] = null;
          }
        }
        await refreshMetricsData();
      }
      showEditModal = false;
      editBlockData = null;
    } catch (e) {
      console.error("Ошибка редактирования:", e);
      formError = "Не удалось сохранить";
    }
  }

  async function removeBlock(blockId) {
    if (!confirm("Удалить блок?")) return;
    try {
      await deleteDashboardBlock(blockId);
      blocks = blocks.filter((b) => b.id !== blockId);
      saveOrder();
      delete metricsData[blockId];
      metricsData = { ...metricsData };
    } catch (e) {
      console.error("Ошибка удаления:", e);
      alert("Не удалось удалить");
    }
  }
</script>

{#if loading}
  <div class="text-center mt-20 text-gray-600 dark:text-gray-300">
    Загрузка дашборда…
  </div>
{:else if loadError && !dashboard}
  <div class="text-red-500 mt-6 ml-6">{loadError}</div>
{:else}
  <div class="p-6 space-y-6 max-w-7xl mx-auto">
    <!-- Заголовок + выбор диапазона -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">
        Дашборд: {dashboard.title}
      </h1>
      <div class="flex items-center space-x-2">
        <span class="text-gray-700 dark:text-gray-300">Диапазон:</span>
        <Select
          bind:value={selectedRange}
          items={TIME_RANGES.map((tr) => ({ value: tr.value, name: tr.label }))}
          class="w-32 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
        />
      </div>
    </div>

    {#if loadError}
      <div class="text-red-500">{loadError}</div>
    {/if}

    <!-- Сетка: максимум 2 колонки -->
    <div class="blocks-grid">
      {#each blocks as block, idx (block.id)}
        <div
          role="button"
          tabindex="0"
          class="relative group bg-white dark:bg-gray-800 w-full h-[32rem] flex flex-col transition-all"
          draggable="true"
          animate:flip={{ duration: 200 }}
          on:dragstart={(e) => onDragStart(e, idx)}
          on:dragover={onDragOver}
          on:drop={(e) => onDrop(e, idx)}
        >
          <!-- Edit/Delete -->
          <div
            class="absolute top-2 right-2 flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <button
              type="button"
              class="p-1 bg-yellow-100 dark:bg-yellow-700 text-yellow-700 dark:text-yellow-100 rounded hover:bg-yellow-200 dark:hover:bg-yellow-600"
              on:click={() => openEditModal(block)}
              aria-label={`Редактировать «${block.title}»`}
            >
              <CogOutline class="h-5 w-5" />
            </button>
            <button
              type="button"
              class="p-1 bg-red-100 dark:bg-red-700 text-red-700 dark:text-red-100 rounded hover:bg-red-200 dark:hover:bg-red-600"
              on:click={() => removeBlock(block.id)}
              aria-label={`Удалить «${block.title}»`}
            >
              <TrashBinOutline class="h-5 w-5" />
            </button>
          </div>

          <!-- Title + Container -->
          <div class="px-4 pt-6">
            <h2 class="text-lg font-medium text-gray-800 dark:text-gray-100">
              {block.title}
            </h2>
            <div class="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {#if block.container_id}
                {containersMap[block.container_id]}
              {/if}
            </div>
          </div>

          <!-- Content: Diagram or Table -->
          <div class="p-4 flex-1">
            {#if block.type === "diagram"}
              <DiagramBlock
                class="w-full h-full"
                title=""
                data={metricsData[block.id] || []}
                unit={block.unit}
                maxY={maxYMap[block.id]}
              />
            {:else}
              <ContainerTableBlock
                class="w-full h-full overflow-auto"
                title=""
                query={block.prometheus_query}
                instance={get(selected_node).hostname || get(selected_node).ip}
                unit={block.unit}
                metric_type={block.metric_type}
                reloadSignal={reloadCounter}
              />
            {/if}
          </div>
        </div>
      {/each}

      <!-- Добавить блок -->
      <button
        type="button"
        class="w-full h-[32rem] flex flex-col items-center justify-center
               bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300
               cursor-pointer hover:shadow-lg transition-all"
        on:click={openAddModal}
      >
        <PlusOutline class="h-10 w-10 mb-2" />
        <span class="text-lg">Добавить блок</span>
      </button>
    </div>
  </div>
{/if}

<!-- Modal Add -->
<Modal bind:open={showAddModal} size="md" placement="center">
  <form class="flex flex-col space-y-4 p-4">
    <h3 class="text-xl font-medium text-gray-900 dark:text-white">
      Добавить блок
    </h3>
    {#if formError}
      <div class="text-sm text-red-600">{formError}</div>
    {/if}

    <Label class="space-y-2">
      <span>Заголовок</span>
      <Input
        type="text"
        bind:value={formTitle}
        placeholder="Название"
        required
      />
    </Label>

    <Label class="space-y-2">
      <span>Контейнер</span>
      <div class="flex space-x-2">
        <Select
          class="flex-1"
          bind:value={formContainerId}
          items={containersList.map((c) => ({
            value: c.id,
            name: `${c.name} (${c.image})`,
          }))}
          on:focus={loadContainers}
        />
        <Input
          type="text"
          placeholder="Поиск..."
          class="w-32"
          bind:value={containerSearch}
          on:input={loadContainers}
        />
      </div>
    </Label>

    <Label class="space-y-2">
      <span>Метрика</span>
      <Select
        bind:value={formMetricType}
        items={[
          { value: "cpu", name: "CPU (%)" },
          { value: "memory", name: "RAM (ГБ)" },
          { value: "network_in", name: "Сеть In (МБ/с)" },
          { value: "network_out", name: "Сеть Out (МБ/с)" },
          { value: "disk", name: "Disk (ГБ)" },
        ]}
        required
      />
    </Label>

    <div class="flex justify-end space-x-2 pt-2">
      <Button color="gray" on:click={() => (showAddModal = false)}>
        Отмена
      </Button>
      <Button
        on:click={(e) => {
          e.preventDefault();
          submitAdd();
        }}
      >
        Создать
      </Button>
    </div>
  </form>
</Modal>

<!-- Modal Edit -->
<Modal bind:open={showEditModal} size="md" placement="center">
  <form class="flex flex-col space-y-4 p-4">
    <h3 class="text-xl font-medium text-gray-900 dark:text-white">
      Редактировать блок
    </h3>
    {#if formError}
      <div class="text-sm text-red-600">{formError}</div>
    {/if}

    <Label class="space-y-2">
      <span>Заголовок</span>
      <Input
        type="text"
        bind:value={formTitle}
        placeholder="Название"
        required
      />
    </Label>

    <Label class="space-y-2">
      <span>Контейнер</span>
      <div class="flex space-x-2">
        <Select
          class="flex-1"
          bind:value={formContainerId}
          items={containersList.map((c) => ({
            value: c.id,
            name: `${c.name} (${c.image})`,
          }))}
          on:focus={loadContainers}
        />
        <Input
          type="text"
          placeholder="Поиск..."
          class="w-32"
          bind:value={containerSearch}
          on:input={loadContainers}
        />
      </div>
    </Label>

    <Label class="space-y-2">
      <span>Метрика</span>
      <Select
        bind:value={formMetricType}
        items={[
          { value: "cpu", name: "CPU (%)" },
          { value: "memory", name: "RAM (ГБ)" },
          { value: "network_in", name: "Сеть In (МБ/с)" },
          { value: "network_out", name: "Сеть Out (МБ/с)" },
          { value: "disk", name: "Disk (ГБ)" },
        ]}
        required
      />
    </Label>

    <div class="flex justify-end space-x-2 pt-2">
      <Button color="gray" on:click={() => (showEditModal = false)}>
        Отмена
      </Button>
      <Button
        on:click={(e) => {
          e.preventDefault();
          submitEdit();
        }}
      >
        Сохранить
      </Button>
    </div>
  </form>
</Modal>

<style>
  .blocks-grid {
    display: grid;
    gap: 1.5rem;
    /* Максимум 2 колонки, при узком экране — 1 колонка */
    grid-template-columns: repeat(2, 1fr);
  }
  @media (max-width: 768px) {
    .blocks-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
