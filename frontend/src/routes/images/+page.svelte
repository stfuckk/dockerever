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
  import { getImages, deleteImage } from "$lib/api/docker_ext";

  let images = [];
  let loading = true;
  let loadError = "";

  let copySuccess = {};

  // Модалки
  let showConfirmModal = false;
  let toDeleteImage = null;

  let showErrorModal = false;
  let errorMessage = "";

  async function loadImages() {
    loading = true;
    loadError = "";
    try {
      images = await getImages();
    } catch (e) {
      console.error("Ошибка при загрузке образов:", e);
      loadError = "Не удалось получить список образов";
      images = [];
    } finally {
      loading = false;
    }
  }

  function openConfirmModal(img) {
    toDeleteImage = img;
    showConfirmModal = true;
  }

  async function runDeleteImage() {
    if (!toDeleteImage) return;
    try {
      await deleteImage(toDeleteImage.id);
      await loadImages();
    } catch (err) {
      errorMessage = err.message || "Ошибка при удалении образа";
      showErrorModal = true;
    } finally {
      showConfirmModal = false;
      toDeleteImage = null;
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

  onMount(loadImages);
</script>

<div class="p-6 max-w-5xl mx-auto">
  <h1 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
    Docker Images
  </h1>

  {#if loading}
    <div class="text-gray-500">Загрузка образов…</div>
  {:else if loadError}
    <div class="text-red-500">{loadError}</div>
  {:else}
    <div class="overflow-x-auto">
      <Table hoverable={true} class="min-w-[600px]">
        <TableHead>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Название (repo:tag)
          </TableHeadCell>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            ID
          </TableHeadCell>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Создан
          </TableHeadCell>
          <TableHeadCell
            class="px-2 py-1 border border-gray-200 dark:border-gray-700"
          >
            Действия
          </TableHeadCell>
        </TableHead>
        <TableBody>
          {#each images as img}
            <TableBodyRow>
              <!-- repo:tag -->
              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                {img.repo_tag}
              </TableBodyCell>

              <!-- Сокращённый ID + кнопка копирования -->
              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                <div class="flex items-center space-x-1">
                  <span class="font-mono text-sm">{img.id.slice(0, 12)}…</span>
                  <button
                    class="p-1 text-gray-500 hover:text-gray-700"
                    on:click={() => copyToClipboard(img.id, `img:${img.id}`)}
                  >
                    {#if copySuccess[`img:${img.id}`]}
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
                {new Date(img.created).toLocaleString()}
              </TableBodyCell>

              <!-- Кнопка удаления -->
              <TableBodyCell
                class="px-2 py-1 border border-gray-200 dark:border-gray-700"
              >
                <Button
                  size="xs"
                  color="red"
                  on:click={() => openConfirmModal(img)}
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
      Удалить образ «{toDeleteImage?.repo_tag}»?
    </h3>
    <div class="flex justify-end space-x-2">
      <Button
        color="gray"
        size="sm"
        on:click={() => (showConfirmModal = false)}
      >
        Отмена
      </Button>
      <Button color="red" size="sm" on:click={runDeleteImage}>Да</Button>
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
