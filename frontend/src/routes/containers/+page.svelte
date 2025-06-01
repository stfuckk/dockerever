<script>
  import { onMount } from "svelte";
  import { get } from "svelte/store";
  import { page } from "$app/stores";
  import { selected_node } from "$lib/stores/selected_node";
  import {
    Table,
    TableHead,
    TableHeadCell,
    TableBody,
    TableBodyRow,
    TableBodyCell,
    Button,
    Modal,
    Label,
    Input,
    Datepicker,
  } from "flowbite-svelte";
  import {
    PlayOutline,
    PauseOutline,
    TerminalOutline,
    ClipboardListOutline,
    CheckOutline,
    TrashBinOutline,
    DownloadOutline,
    CloseOutline,
  } from "flowbite-svelte-icons";
  import { getContainers } from "$lib/api/docker";
  import { authFetch } from "$lib/api/auth";

  let containers = $state([]);
  let loading = $state(true);
  let loadError = $state("");

  // Пришел ли из URL параметр ?search=…
  let searchQuery = $state("");

  // Для логов
  let showLogsModal = $state(false);
  let activeContainer = $state(null);
  let startDate = $state(new Date());
  let endDate = $state(new Date());
  let startTime = $state("00:00");
  let endTime = $state("23:59");
  let logsContent = $state("");

  // Для терминала
  let showTermModal = $state(false);
  let termOutput = $state("");
  let termInput = $state("");

  // Подтверждение stop/delete
  let showConfirmModal = $state(false);
  let confirmActionType = $state("");
  let confirmContainer = $state(null);

  // Для состояния копирования ID
  let copySuccess = $state({});

  async function loadContainers() {
    loading = true;
    loadError = "";
    try {
      const res = await getContainers(searchQuery.trim());
      containers = res.containers || [];
    } catch (e) {
      console.error("Ошибка при загрузке контейнеров:", e);
      loadError = "Не удалось получить список контейнеров";
      containers = [];
    } finally {
      loading = false;
    }
  }

  function confirmAction(type, container) {
    confirmActionType = type;
    confirmContainer = container;
    showConfirmModal = true;
  }

  async function runConfirmedAction() {
    if (!confirmContainer) return;
    if (confirmActionType === "stop") {
      await actuallyToggle(confirmContainer);
    } else if (confirmActionType === "delete") {
      await actuallyDelete(confirmContainer);
    }
    showConfirmModal = false;
    confirmContainer = null;
    confirmActionType = "";
  }

  async function actuallyToggle(container) {
    const action = container.status === "running" ? "stop" : "start";
    try {
      const endpoint =
        action === "stop"
          ? `/api/v1/docker/containers/${container.id}/stop`
          : `/api/v1/docker/containers/${container.id}/start`;
      await authFetch(endpoint, { method: "POST" });
      await loadContainers();
    } catch {
      alert(
        "Не удалось " +
          (action === "stop" ? "остановить" : "запустить") +
          " контейнер"
      );
    }
  }

  async function actuallyDelete(container) {
    try {
      await authFetch(`/api/v1/docker/containers/${container.id}`, {
        method: "DELETE",
      });
      await loadContainers();
    } catch {
      alert("Не удалось удалить контейнер");
    }
  }

  function openLogs(container) {
    activeContainer = container;
    startDate = new Date();
    endDate = new Date();
    startTime = "00:00";
    endTime = "23:59";
    logsContent = "";
    showLogsModal = true;
    fetchLogs();
  }

  async function fetchLogs() {
    if (!activeContainer) return;
    try {
      const params = new URLSearchParams();
      if (startDate instanceof Date) {
        params.set("start_date", startDate.toISOString().slice(0, 10));
      }
      if (startTime) {
        params.set("start_time", startTime);
      }
      if (endDate instanceof Date) {
        params.set("end_date", endDate.toISOString().slice(0, 10));
      }
      if (endTime) {
        params.set("end_time", endTime);
      }

      const url = `/api/v1/docker/containers/${activeContainer.id}/logs?${params.toString()}`;
      const res = await authFetch(url);
      const data = await res.json();
      logsContent = data.logs || "";
    } catch (e) {
      console.error("Ошибка при загрузке логов:", e);
      logsContent = "Ошибка при загрузке логов";
    }
  }

  function downloadLogs() {
    const blob = new Blob([logsContent], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${activeContainer.name}-logs.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function openTerminal(container) {
    activeContainer = container;
    termOutput = "";
    termInput = "";
    showTermModal = true;
  }

  async function sendCommand() {
    if (!activeContainer || !termInput.trim()) return;
    try {
      const url = `/api/v1/docker/containers/${activeContainer.id}/exec?command=${encodeURIComponent(
        termInput
      )}`;
      const res = await authFetch(url, { method: "POST" });
      const data = await res.json();
      termOutput += `$ ${termInput}\n${data.output}\n`;
      termInput = "";
    } catch (e) {
      console.error("Ошибка выполнения команды:", e);
      termOutput += "Ошибка выполнения команды\n";
    }
  }

  function copyId(fullId) {
    navigator.clipboard.writeText(fullId).then(() => {
      copySuccess[fullId] = true;
      setTimeout(() => {
        copySuccess[fullId] = false;
      }, 2000);
    });
  }

  onMount(() => {
    // Проверяем, есть ли в URL параметр ?search=…
    const params = get(page).url.searchParams;
    const fromSearch = params.get("search") || "";
    if (fromSearch.trim()) {
      searchQuery = fromSearch;
    }
    loadContainers();
  });
</script>

<div class="p-6 max-w-7xl mx-auto">
  <h1 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
    Контейнеры: {$selected_node?.hostname ?? "—"}
  </h1>

  <div class="mb-4 flex space-x-2">
    <Input
      placeholder="Поиск по имени..."
      bind:value={searchQuery}
      on:keydown={(e) => {
        if (e.key === "Enter") loadContainers();
      }}
    />
    <Button on:click={loadContainers}>Поиск</Button>
    <Button
      outline={true}
      color="purple"
      on:click={() => {
        searchQuery = "";
        loadContainers();
      }}
    >
      Сброс
    </Button>
  </div>

  {#if loading}
    <div class="text-gray-500">Загрузка контейнеров…</div>
  {:else if loadError}
    <div class="text-red-500">{loadError}</div>
  {:else}
    <div class="overflow-x-auto">
      <Table hoverable={true} class="min-w-[800px]">
        <TableHead>
          <!-- Восстановили границы: border, border-gray-200 и dark:border-gray-700 -->
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Статус
          </TableHeadCell>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Название
          </TableHeadCell>
          <TableHeadCell
            class="px-2 py-1 text-center border border-gray-200 dark:border-gray-700"
          >
            ID
          </TableHeadCell>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Образ
          </TableHeadCell>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Сеть
          </TableHeadCell>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Volumes
          </TableHeadCell>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Действия
          </TableHeadCell>
        </TableHead>
        <TableBody>
          {#each containers as cont}
            <TableBodyRow>
              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                {#if cont.status === "running"}
                  <span class="text-green-600 font-semibold">Running</span>
                {:else}
                  <span class="text-red-600 font-semibold">Stopped</span>
                {/if}
              </TableBodyCell>

              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                {cont.name}
              </TableBodyCell>

              <!-- ID: центр + первые 5 символов + кнопка копирования -->
              <TableBodyCell
                class="px-2 py-1 text-center border border-gray-200 dark:border-gray-700"
              >
                <div class="relative inline-block">
                  <input
                    id={"copy-" + cont.id}
                    type="text"
                    class="bg-transparent border-none text-center text-sm w-20"
                    value={cont.id.slice(0, 5) + "…"}
                    disabled
                    readonly
                  />
                  <button
                    class="absolute right-0 top-1/2 -translate-y-1/2 p-[-2] text-gray-500 hover:text-gray-700"
                    onclick={() => copyId(cont.id)}
                  >
                    {#if copySuccess[cont.id]}
                      <CheckOutline class="w-4 h-4 text-blue-600" />
                    {:else}
                      <ClipboardListOutline class="w-4 h-4" />
                    {/if}
                  </button>
                </div>
              </TableBodyCell>

              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                {cont.image}
              </TableBodyCell>
              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                {cont.networks || "—"}
              </TableBodyCell>
              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                {#if cont.volumes && cont.volumes.length > 0}
                  <div class="max-h-16 overflow-auto text-sm">
                    {#each cont.volumes as vol}
                      <div>{vol}</div>
                    {/each}
                  </div>
                {:else}
                  —
                {/if}
              </TableBodyCell>

              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                <div class="grid grid-cols-1 gap-1">
                  <Button
                    size="xs"
                    outline={true}
                    color={cont.status === "running" ? "red" : "green"}
                    on:click={() => confirmAction("stop", cont)}
                  >
                    {#if cont.status === "running"}
                      <PauseOutline class="mr-1 w-4 h-4" /> Стоп
                    {:else}
                      <PlayOutline class="mr-1 w-4 h-4" /> Старт
                    {/if}
                  </Button>

                  <Button
                    size="xs"
                    outline={true}
                    on:click={() => openLogs(cont)}
                  >
                    <ClipboardListOutline class="mr-1 w-4 h-4" /> Логи
                  </Button>

                  <Button
                    size="xs"
                    outline={true}
                    color="blue"
                    on:click={() => openTerminal(cont)}
                  >
                    <TerminalOutline class="mr-1 w-4 h-4" /> Команда
                  </Button>

                  <Button
                    size="xs"
                    color="red"
                    on:click={() => confirmAction("delete", cont)}
                  >
                    <TrashBinOutline class="mr-1 w-4 h-4" /> Удалить
                  </Button>
                </div>
              </TableBodyCell>
            </TableBodyRow>
          {/each}
        </TableBody>
      </Table>
    </div>
  {/if}
</div>

<!-- Модалка подтверждения Stop/Delete -->
<Modal
  bind:open={showConfirmModal}
  size="sm"
  placement="center"
  showClose={false}
>
  <!-- Просто окно с текстом и кнопками, без дефолтного хедера -->
  <div class="p-4">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
      {#if confirmActionType === "stop"}
        Остановить контейнер «{confirmContainer?.name}»?
      {:else}
        Удалить контейнер «{confirmContainer?.name}»?
      {/if}
    </h3>
    <div class="flex justify-end space-x-2">
      <Button
        color="gray"
        size="sm"
        on:click={() => (showConfirmModal = false)}
      >
        Отмена
      </Button>
      <Button color="red" size="sm" on:click={runConfirmedAction}>Да</Button>
    </div>
  </div>
</Modal>

<!-- Модалка для логов -->
<Modal bind:open={showLogsModal} size="lg" placement="center" showClose={false}>
  <svelte:fragment slot="header">
    <div class="flex justify-between items-center w-full px-4 py-2">
      <h3 class="text-xl font-medium text-gray-900 dark:text-white">
        Логи: {activeContainer?.name}
      </h3>
    </div>
  </svelte:fragment>

  <div class="p-4">
    <div class="mb-4 grid grid-cols-2 gap-4">
      <div>
        <Label>Дата с:</Label>
        <Datepicker bind:value={startDate} dateFormat="Y-m-d" />
      </div>
      <div>
        <Label>Дата до:</Label>
        <Datepicker bind:value={endDate} dateFormat="Y-m-d" />
      </div>
      <div>
        <Label>Время с:</Label>
        <Input type="time" bind:value={startTime} />
      </div>
      <div>
        <Label>Время до:</Label>
        <Input type="time" bind:value={endTime} />
      </div>
    </div>

    <div class="mb-4 text-right">
      <Button color="blue" size="sm" on:click={fetchLogs}>Показать</Button>
    </div>

    <div class="h-80 overflow-auto bg-gray-100 dark:bg-gray-800 p-2 rounded">
      <pre class="text-xs text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
{logsContent}
      </pre>
    </div>

    <div class="mt-4 flex justify-end space-x-2">
      <Button color="gray" on:click={() => (showLogsModal = false)}>
        Закрыть
      </Button>
      <Button color="blue" on:click={downloadLogs}>
        <DownloadOutline class="mr-1 w-4 h-4" /> Скачать .txt
      </Button>
    </div>
  </div>
</Modal>

<!-- Модалка для терминала -->
<Modal bind:open={showTermModal} size="lg" placement="center" showClose={false}>
  <svelte:fragment slot="header">
    <div class="flex justify-between items-center w-full px-4 py-2">
      <h3 class="text-xl font-medium text-gray-900 dark:text-white">
        Терминал: {activeContainer?.name}
      </h3>
    </div>
  </svelte:fragment>

  <div class="p-4 flex flex-col space-y-4">
    <div
      class="h-56 overflow-auto bg-black text-green-400 p-2 rounded font-mono text-sm"
    >
      <pre class="whitespace-pre-wrap">{termOutput}</pre>
    </div>

    <div class="flex space-x-2">
      <Input
        class="flex-1"
        placeholder="Введите команду..."
        bind:value={termInput}
        on:keydown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            sendCommand();
          }
        }}
      />
      <Button color="green" on:click={sendCommand}>Ввод</Button>
    </div>

    <div class="text-xs text-gray-500">
      * Введите команды для <code>docker exec</code>. Например:
      <code>ls /app</code>
    </div>
  </div>
</Modal>
