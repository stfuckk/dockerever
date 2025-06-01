<script>
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";

  import {
    getUserDashboards,
    createDashboard,
    updateDashboard,
    deleteDashboard,
  } from "$lib/api/dashboards";

  import {
    Table,
    TableHead,
    TableHeadCell,
    TableBody,
    TableBodyRow,
    TableBodyCell,
    Modal,
    Label,
    Input,
    Button,
  } from "flowbite-svelte";

  import {
    PlusOutline,
    TrashBinOutline,
    EyeOutline,
    PenOutline,
    CheckOutline,
    CloseOutline,
  } from "flowbite-svelte-icons";

  let dashboards = [];
  let loading = true;
  let loadError = "";

  // ===== Создать дашборд =====
  let showCreateModal = false;
  let newTitle = "";
  let newDescription = "";

  // ===== Удалить дашборд =====
  let showDeleteModal = false;
  let deletingId = null;

  // ===== Inline-редактирование =====
  let editingTitle = {};
  let editingDesc = {};
  let tempTitle = {};
  let tempDesc = {};

  async function loadList() {
    loading = true;
    loadError = "";
    try {
      dashboards = await getUserDashboards();
      dashboards.forEach((d) => {
        editingTitle[d.id] = false;
        editingDesc[d.id] = false;
        tempTitle[d.id] = d.title;
        tempDesc[d.id] = d.description;
      });
    } catch (e) {
      console.error("Ошибка при загрузке списка дашбордов:", e);
      loadError = "Не удалось получить список дашбордов";
    } finally {
      loading = false;
    }
  }

  onMount(loadList);

  // ===== Функция создания нового дашборда =====
  async function submitCreate() {
    if (!newTitle.trim()) {
      alert("Введите имя дашборда");
      return;
    }
    const payload = {
      title: newTitle,
      description: newDescription,
      system: false,
      blocks: [],
    };
    try {
      const created = await createDashboard(payload);
      dashboards = [...dashboards, created];
      editingTitle[created.id] = false;
      editingDesc[created.id] = false;
      tempTitle[created.id] = created.title;
      tempDesc[created.id] = created.description;
      newTitle = "";
      newDescription = "";
      showCreateModal = false;
    } catch (e) {
      console.error("Ошибка при создании дашборда:", e);
      // alert отменили по задаче
    }
  }

  // ===== Переход к просмотру/редактированию конкретного дашборда =====
  function openDashboard(title) {
    goto(`/dashboards/${encodeURIComponent(title)}`);
  }

  // ===== Inline-edit «Название» =====
  function startEditTitle(id, current) {
    editingTitle[id] = true;
    tempTitle[id] = current;
  }
  async function saveTitle(id) {
    const newVal = tempTitle[id].trim();
    if (!newVal) {
      tempTitle[id] = dashboards.find((d) => d.id === id)?.title ?? "";
      editingTitle[id] = false;
      return;
    }
    try {
      const updated = await updateDashboard(id, { title: newVal });
      dashboards = dashboards.map((d) =>
        d.id === id ? { ...d, title: updated.title } : d
      );
    } catch (e) {
      console.error("Ошибка при обновлении названия:", e);
      // без alert
    } finally {
      editingTitle[id] = false;
    }
  }
  function cancelEditTitle(id, original) {
    tempTitle[id] = original;
    editingTitle[id] = false;
  }

  // ===== Inline-edit «Описание» =====
  function startEditDesc(id, current) {
    editingDesc[id] = true;
    tempDesc[id] = current;
  }
  async function saveDesc(id) {
    try {
      const updated = await updateDashboard(id, {
        description: tempDesc[id].trim(),
      });
      dashboards = dashboards.map((d) =>
        d.id === id ? { ...d, description: updated.description } : d
      );
    } catch (e) {
      console.error("Ошибка при обновлении описания:", e);
      // без alert
    } finally {
      editingDesc[id] = false;
    }
  }
  function cancelEditDesc(id, original) {
    tempDesc[id] = original;
    editingDesc[id] = false;
  }

  // ===== Удаление дашборда =====
  function openDeleteModal(id) {
    deletingId = id;
    showDeleteModal = true;
  }
  async function confirmDelete() {
    try {
      await deleteDashboard(deletingId);
      dashboards = dashboards.filter((d) => d.id !== deletingId);
    } catch (e) {
      console.error("Ошибка при удалении дашборда:", e);
      // без alert
    } finally {
      showDeleteModal = false;
      deletingId = null;
    }
  }
  function cancelDelete() {
    showDeleteModal = false;
    deletingId = null;
  }
</script>

{#if loading}
  <div class="text-center mt-16 text-gray-600 dark:text-gray-300">
    Загрузка списка дашбордов…
  </div>
{:else if loadError}
  <div class="text-red-500 mt-6 ml-6">{loadError}</div>
{:else}
  <div class="p-6 space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">
        Мои дашборды
      </h1>
      <Button on:click={() => (showCreateModal = true)}>
        <PlusOutline class="h-5 w-5 mr-1" /> Новый дашборд
      </Button>
    </div>

    <Table hoverable={true} class="w-full">
      <TableHead>
        <TableHeadCell>Название</TableHeadCell>
        <TableHeadCell>Описание</TableHeadCell>
        <TableHeadCell>Владелец</TableHeadCell>
        <TableHeadCell class="text-center">Действия</TableHeadCell>
      </TableHead>
      <TableBody>
        {#each dashboards as db (db.id)}
          {#if !db.system}
            <TableBodyRow
              class="hover:bg-gray-600/10 dark:hover:bg-gray-600/10"
            >
              <!-- Название (inline‐editable) -->
              <TableBodyCell>
                {#if editingTitle[db.id]}
                  <div class="flex items-center space-x-1">
                    <Input
                      bind:value={tempTitle[db.id]}
                      on:keydown={(e) => {
                        if (e.key === "Enter") {
                          saveTitle(db.id);
                        } else if (e.key === "Escape") {
                          cancelEditTitle(db.id, db.title);
                        }
                      }}
                      on:blur={() => saveTitle(db.id)}
                    />
                    <button
                      type="button"
                      class="p-1 text-green-600 dark:text-green-400 hover:text-green-800 dark:hover:text-green-200"
                      on:click={() => saveTitle(db.id)}
                      aria-label="Сохранить название"
                    >
                      <CheckOutline class="h-5 w-5" />
                    </button>
                    <button
                      type="button"
                      class="p-1 text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
                      on:click={() => cancelEditTitle(db.id, db.title)}
                      aria-label="Отменить"
                    >
                      <CloseOutline class="h-5 w-5" />
                    </button>
                  </div>
                {:else}
                  <div class="flex items-center space-x-1">
                    <button
                      type="button"
                      class="text-left text-blue-600 dark:text-blue-400 hover:underline"
                      on:click={() => openDashboard(db.title)}
                    >
                      {db.title}
                    </button>
                    <button
                      type="button"
                      class="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
                      on:click={() => startEditTitle(db.id, db.title)}
                      aria-label="Редактировать название"
                    >
                      <PenOutline class="h-5 w-5" />
                    </button>
                  </div>
                {/if}
              </TableBodyCell>

              <!-- Описание (inline‐editable) -->
              <TableBodyCell>
                {#if editingDesc[db.id]}
                  <div class="flex items-center space-x-1">
                    <Input
                      bind:value={tempDesc[db.id]}
                      on:keydown={(e) => {
                        if (e.key === "Enter") {
                          saveDesc(db.id);
                        } else if (e.key === "Escape") {
                          cancelEditDesc(db.id, db.description);
                        }
                      }}
                      on:blur={() => saveDesc(db.id)}
                    />
                    <button
                      type="button"
                      class="p-1 text-green-600 dark:text-green-400 hover:text-green-800 dark:hover:text-green-200"
                      on:click={() => saveDesc(db.id)}
                      aria-label="Сохранить описание"
                    >
                      <CheckOutline class="h-5 w-5" />
                    </button>
                    <button
                      type="button"
                      class="p-1 text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
                      on:click={() => cancelEditDesc(db.id, db.description)}
                      aria-label="Отменить"
                    >
                      <CloseOutline class="h-5 w-5" />
                    </button>
                  </div>
                {:else}
                  <div class="flex items-center space-x-1">
                    <span class="text-gray-700 dark:text-gray-300"
                      >{db.description}</span
                    >
                    <button
                      type="button"
                      class="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
                      on:click={() => startEditDesc(db.id, db.description)}
                      aria-label="Редактировать описание"
                    >
                      <PenOutline class="h-5 w-5" />
                    </button>
                  </div>
                {/if}
              </TableBodyCell>

              <!-- Владелец -->
              <TableBodyCell>{db.owner_username}</TableBodyCell>

              <!-- Действия -->
              <TableBodyCell class="flex justify-center space-x-2">
                <button
                  type="button"
                  on:click={() => openDashboard(db.title)}
                  class="p-1 text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white"
                  aria-label="Открыть дашборд"
                >
                  <EyeOutline class="h-5 w-5" />
                </button>
                <button
                  type="button"
                  on:click={() => openDeleteModal(db.id)}
                  class="p-1 text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
                  aria-label="Удалить дашборд"
                >
                  <TrashBinOutline class="h-5 w-5" />
                </button>
              </TableBodyCell>
            </TableBodyRow>
          {/if}
        {/each}
      </TableBody>
    </Table>
  </div>

  <!-- ===== МОДАЛЬНОЕ ОКНО: СОЗДАНИЕ ДАШБОРДА ===== -->
  <!-- Добавили class="mt-24", чтобы окно не «утонуло» под шапкой -->
  <Modal bind:open={showCreateModal} size="sm" placement="center" class="mt-24">
    <form class="flex flex-col space-y-4 p-4">
      <h3 class="text-xl font-medium text-gray-900 dark:text-white">
        Новый дашборд
      </h3>

      <Label class="space-y-2">
        <span>Название</span>
        <Input
          type="text"
          bind:value={newTitle}
          placeholder="Введите название"
          required
        />
      </Label>

      <Label class="space-y-2">
        <span>Описание (необязательно)</span>
        <Input
          type="text"
          bind:value={newDescription}
          placeholder="Введите описание"
        />
      </Label>

      <div class="flex justify-end space-x-2 pt-2">
        <Button color="gray" on:click={() => (showCreateModal = false)}>
          Отмена
        </Button>
        <Button
          on:click={(e) => {
            e.preventDefault();
            submitCreate();
          }}
        >
          Создать
        </Button>
      </div>
    </form>
  </Modal>

  <!-- ===== МОДАЛЬНОЕ ОКНО: УДАЛЕНИЕ ДАШБОРДА ===== -->
  <Modal bind:open={showDeleteModal} size="xs" placement="center" class="mt-24">
    <div class="p-4">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
        Удалить дашборд?
      </h3>
      <div class="flex justify-end space-x-2">
        <Button color="gray" on:click={cancelDelete}>Отмена</Button>
        <Button color="red" on:click={confirmDelete}>Удалить</Button>
      </div>
    </div>
  </Modal>
{/if}
