<script>
  import { onMount } from "svelte";
  import {
    Table,
    TableHead,
    TableHeadCell,
    TableBody,
    TableBodyRow,
    TableBodyCell,
    Button,
    Modal,
  } from "flowbite-svelte";
  import { ClipboardListOutline, CheckOutline } from "flowbite-svelte-icons";
  import { getVolumes, deleteVolume } from "$lib/api/docker_ext";

  let volumes = [];
  let loading = true;
  let loadError = "";

  // Для состояния «скопировано» у каждого тома и каждой точки монтирования
  let copySuccess = {};

  // Для модальной ошибки удаления
  let showErrorModal = false;
  let errorMessage = "";

  // Для модальной «Подтверждение удаления»
  let showConfirmModal = false;
  let toDeleteVolume = null;

  async function loadVolumes() {
    loading = true;
    loadError = "";
    try {
      volumes = await getVolumes();
    } catch (e) {
      console.error("Ошибка при загрузке томов:", e);
      loadError = "Не удалось получить список томов";
      volumes = [];
    } finally {
      loading = false;
    }
  }

  function openConfirmModal(vol) {
    toDeleteVolume = vol;
    showConfirmModal = true;
  }

  async function runDeleteVolume() {
    if (!toDeleteVolume) return;
    try {
      await deleteVolume(toDeleteVolume.name);
      await loadVolumes();
    } catch (err) {
      errorMessage = err.message || "Ошибка при удалении тома";
      showErrorModal = true;
    } finally {
      showConfirmModal = false;
      toDeleteVolume = null;
    }
  }

  function copyToClipboard(text, key) {
    navigator.clipboard.writeText(text).then(() => {
      copySuccess[key] = true;
      setTimeout(() => {
        copySuccess[key] = false;
      }, 2000);
    });
  }

  /**
   * Сокращение mountpoint: находим "volumes/",
   * берём от начала "volumes/" плюс 5 символов дальше и добавляем "…"
   */
  function truncateMountpoint(fullPath) {
    const marker = "volumes/";
    const idx = fullPath.indexOf(marker);
    if (idx === -1) {
      return fullPath.length > 20 ? fullPath.slice(0, 20) + "…" : fullPath;
    }
    const start = idx + marker.length;
    const snippet = fullPath.slice(idx, start + 5);
    return snippet.length < fullPath.length ? snippet + "…" : snippet;
  }

  onMount(loadVolumes);
</script>

<div class="p-6 max-w-5xl mx-auto">
  <h1 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
    Docker Volumes
  </h1>

  {#if loading}
    <div class="text-gray-500">Загрузка томов…</div>
  {:else if loadError}
    <div class="text-red-500">{loadError}</div>
  {:else}
    <div class="overflow-x-auto">
      <Table hoverable={true} class="min-w-[600px]">
        <TableHead>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Имя тома
          </TableHeadCell>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Создан
          </TableHeadCell>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Точка монтирования
          </TableHeadCell>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Scope
          </TableHeadCell>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Действия
          </TableHeadCell>
        </TableHead>
        <TableBody>
          {#each volumes as vol}
            <TableBodyRow>
              <!-- Сокращённое имя тома + кнопка копирования -->
              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                <div class="flex items-center space-x-1">
                  <span class="text-sm">
                    {vol.name.length > 8
                      ? vol.name.slice(0, 8) + "…"
                      : vol.name}
                  </span>
                  <button
                    class="p-1 text-gray-500 hover:text-gray-700"
                    on:click={() =>
                      copyToClipboard(vol.name, `name:${vol.name}`)}
                  >
                    {#if copySuccess[`name:${vol.name}`]}
                      <CheckOutline class="w-4 h-4 text-blue-600" />
                    {:else}
                      <ClipboardListOutline class="w-4 h-4" />
                    {/if}
                  </button>
                </div>
              </TableBodyCell>

              <!-- Дата создания -->
              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                {new Date(vol.created_at).toLocaleString()}
              </TableBodyCell>

              <!-- Сокращённый mountpoint + кнопка копирования -->
              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                <div class="flex items-center space-x-1">
                  <span class="text-sm"
                    >{truncateMountpoint(vol.mountpoint)}</span
                  >
                  <button
                    class="p-1 text-gray-500 hover:text-gray-700"
                    on:click={() =>
                      copyToClipboard(vol.mountpoint, `mp:${vol.mountpoint}`)}
                  >
                    {#if copySuccess[`mp:${vol.mountpoint}`]}
                      <CheckOutline class="w-4 h-4 text-blue-600" />
                    {:else}
                      <ClipboardListOutline class="w-4 h-4" />
                    {/if}
                  </button>
                </div>
              </TableBodyCell>

              <!-- Scope -->
              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                {vol.scope}
              </TableBodyCell>

              <!-- Кнопка удаления -->
              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                <Button
                  size="xs"
                  color="red"
                  on:click={() => openConfirmModal(vol)}
                >
                  Удалить
                </Button>
              </TableBodyCell>
            </TableBodyRow>
          {/each}
        </TableBody>
      </Table>
    </div>
  {/if}
</div>

<!-- ------------------ -->
<!-- Модалка «Подтвердить удаление» -->
<Modal
  bind:open={showConfirmModal}
  size="sm"
  placement="center"
  showClose={false}
>
  <div class="p-4">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
      Удалить том «{toDeleteVolume?.name.slice(0, 9) + "..."}»?
    </h3>
    <div class="flex justify-end space-x-2">
      <Button
        color="gray"
        size="sm"
        on:click={() => (showConfirmModal = false)}
      >
        Отмена
      </Button>
      <Button color="red" size="sm" on:click={runDeleteVolume}>Да</Button>
    </div>
  </div>
</Modal>

<!-- ------------------ -->
<!-- Модалка ошибки -->
<Modal
  bind:open={showErrorModal}
  size="md"
  placement="center"
  showClose={false}
>
  <div class="p-4">
    <h3 class="text-lg font-medium text-red-600 mb-2">Ошибка</h3>
    <p class="text-sm text-gray-700 dark:text-gray-300 mb-4">{errorMessage}</p>
    <div class="flex justify-end">
      <Button color="gray" size="sm" on:click={() => (showErrorModal = false)}>
        Закрыть
      </Button>
    </div>
  </div>
</Modal>
