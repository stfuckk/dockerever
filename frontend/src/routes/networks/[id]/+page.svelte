<script>
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import { getNetworkContainers } from "$lib/api/docker_ext";
  import { Card, Button, Modal } from "flowbite-svelte";
  import { ClipboardListOutline, CheckOutline } from "flowbite-svelte-icons";

  let networkId = "";
  $: networkId = $page.params.id;

  let containers = [];
  let loading = true;
  let loadError = "";

  // Для состояния «скопировано» у каждого контейнера
  let copySuccess = {};

  // Модалка ошибки удаления сети (если понадобится)
  let showErrorModal = false;
  let errorMessage = "";

  // Если потребуется «Удалить сеть» -> сюда можно передавать
  let showConfirmModal = false;
  let toDeleteNetwork = null;

  async function loadContainersInNetwork() {
    loading = true;
    loadError = "";
    try {
      const resp = await getNetworkContainers(networkId);
      // API выдаёт { network: {...}, containers: [...] }, но нам нужно только список контейнеров
      containers = resp.containers || [];
    } catch (e) {
      console.error("Ошибка при загрузке контейнеров сети:", e);
      loadError = "Не удалось получить контейнеры для этой сети";
      containers = [];
    } finally {
      loading = false;
    }
  }

  function copyToClipboard(text, key) {
    navigator.clipboard.writeText(text).then(() => {
      copySuccess[key] = true;
      setTimeout(() => (copySuccess[key] = false), 2000);
    });
  }

  function goToContainer(name) {
    window.location.href = `/containers?search=${encodeURIComponent(name)}`;
  }

  onMount(loadContainersInNetwork);
</script>

<div class="p-6 max-w-5xl mx-auto">
  <!-- Заголовок: только название сети -->
  <h1 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
    Сеть: {networkId}
  </h1>

  {#if loading}
    <div class="text-gray-500">Загрузка контейнеров сети…</div>
  {:else if loadError}
    <div class="text-red-500">{loadError}</div>
  {:else if containers.length === 0}
    <div class="text-gray-600 dark:text-gray-400">
      В этой сети нет контейнеров.
    </div>
  {:else}
    <!-- Сетка карточек контейнеров: от 1 до 3 столбцов -->
    <div class="grid gap-8 grid-cols-1 sm:grid-cols-2 md:grid-cols-3">
      {#each containers as ctr}
        <Card class="shadow-md dark:bg-gray-800">
          <div class="p-4">
            <h2
              class="text-lg font-semibold text-gray-900 dark:text-white mb-2 overflow-hidden"
            >
              {ctr.name}
            </h2>

            <!-- ID: первые 8 символов + кнопка копирования -->
            <div class="flex items-center space-x-1 mb-1">
              <span class="text-sm text-gray-600 dark:text-gray-400">ID:</span>
              <span class="font-mono text-sm">{ctr.id.slice(0, 8)}…</span>
              <button
                class="p-1 text-gray-500 hover:text-gray-700"
                on:click={() => copyToClipboard(ctr.id, `ctr:${ctr.id}`)}
              >
                {#if copySuccess[`ctr:${ctr.id}`]}
                  <CheckOutline class="w-4 h-4 text-blue-600" />
                {:else}
                  <ClipboardListOutline class="w-4 h-4" />
                {/if}
              </button>
            </div>

            <!-- Статус -->
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Статус:
              {#if ctr.status === "running"}
                <span class="text-green-600 font-semibold">Running</span>
              {:else}
                <span class="text-red-600 font-semibold">Stopped</span>
              {/if}
            </p>
          </div>

          <!-- Кнопка «Перейти к контейнеру» -->
          <div class="p-2 flex justify-end">
            <Button
              size="xs"
              outline={true}
              on:click={() => goToContainer(ctr.name)}
            >
              Перейти к контейнеру
            </Button>
          </div>
        </Card>
      {/each}
    </div>
  {/if}
</div>
