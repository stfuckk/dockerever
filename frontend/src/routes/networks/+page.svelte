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
  import { getNetworks, deleteNetwork } from "$lib/api/docker_ext";
  import { goto } from "$app/navigation";

  let networks = [];
  let loading = true;
  let loadError = "";

  let copySuccess = {};

  // Модалки
  let showConfirmModal = false;
  let toDeleteNetwork = null;

  let showErrorModal = false;
  let errorMessage = "";

  async function loadNetworks() {
    loading = true;
    loadError = "";
    try {
      networks = await getNetworks();
    } catch (e) {
      console.error("Ошибка при загрузке сетей:", e);
      loadError = "Не удалось получить список сетей";
      networks = [];
    } finally {
      loading = false;
    }
  }

  function openConfirmModal(net) {
    toDeleteNetwork = net;
    showConfirmModal = true;
  }

  async function runDeleteNetwork() {
    if (!toDeleteNetwork) return;
    try {
      await deleteNetwork(toDeleteNetwork.id);
      await loadNetworks();
    } catch (err) {
      errorMessage = err.message || "Ошибка при удалении сети";
      showErrorModal = true;
    } finally {
      showConfirmModal = false;
      toDeleteNetwork = null;
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

  function openNetwork(net) {
    goto(`/networks/${encodeURIComponent(net.id)}`);
  }

  onMount(loadNetworks);
</script>

<div class="p-6 max-w-5xl mx-auto">
  <h1 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
    Docker Networks
  </h1>

  {#if loading}
    <div class="text-gray-500">Загрузка сетей…</div>
  {:else if loadError}
    <div class="text-red-500">{loadError}</div>
  {:else}
    <div class="overflow-x-auto">
      <Table hoverable={true} class="min-w-[600px]">
        <TableHead>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Название сети
          </TableHeadCell>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            ID
          </TableHeadCell>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Driver
          </TableHeadCell>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Действия
          </TableHeadCell>
        </TableHead>
        <TableBody>
          {#each networks as net}
            <TableBodyRow>
              <!-- Название сети (клик ведёт на детальную страницу) -->
              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                <button
                  class="text-blue-600 dark:text-blue-400 hover:underline"
                  on:click={() => openNetwork(net)}
                >
                  {net.name}
                </button>
              </TableBodyCell>

              <!-- Сокращённый ID + копирование -->
              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                <div class="flex items-center space-x-1">
                  <span class="font-mono text-sm">{net.id.slice(0, 12)}…</span>
                  <button
                    class="p-1 text-gray-500 hover:text-gray-700"
                    on:click={() => copyToClipboard(net.id, `net:${net.id}`)}
                  >
                    {#if copySuccess[`net:${net.id}`]}
                      <CheckOutline class="w-4 h-4 text-blue-600" />
                    {:else}
                      <ClipboardListOutline class="w-4 h-4" />
                    {/if}
                  </button>
                </div>
              </TableBodyCell>

              <!-- Driver -->
              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                {net.driver}
              </TableBodyCell>

              <!-- Удалить сеть -->
              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                <Button
                  size="xs"
                  color="red"
                  on:click={() => openConfirmModal(net)}
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
      Удалить сеть «{toDeleteNetwork?.name}»?
    </h3>
    <div class="flex justify-end space-x-2">
      <Button
        color="gray"
        size="sm"
        on:click={() => (showConfirmModal = false)}
      >
        Отмена
      </Button>
      <Button color="red" size="sm" on:click={runDeleteNetwork}>Да</Button>
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
