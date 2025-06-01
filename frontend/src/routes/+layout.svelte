<script>
  import "../app.css";
  import NavigationBar from "$lib/global/NavigationBar.svelte";
  import SidebarLayout from "$lib/global/SidebarLayout.svelte";
  import { isAuthorized as authCheck } from "$lib/api/auth";
  import { is_authorized, user } from "$lib/stores/authStore";
  import { selected_node } from "$lib/stores/selected_node";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import MobileNav from "$lib/global/MobileNav.svelte";
  import NodeSelector from "$lib/global/NodeSelector.svelte";
  import { getNodes } from "$lib/api/dashboards";

  // === ОБЯЗАТЕЛЬНОЕ: объявляем реактивные переменные через $state ===
  let nodes = $state([]); // массив серверов
  let nodesLoaded = $state(false); // флаг «список серверов получен»
  let { children } = $props(); // дочерние компоненты, которые будут рендериться в основном контенте
  onMount(async () => {
    // 1) Проверяем, авторизован ли пользователь
    const currentUser = await authCheck();
    if (!currentUser) {
      is_authorized.set(false);
      goto("/login");
      return;
    }
    if (currentUser.must_change_password) {
      is_authorized.set(false);
      goto("/login?reason=must_change_password");
      return;
    }
    // 2) Сохраняем данные пользователя в сторы
    user.set(currentUser);
    is_authorized.set(true);

    // 3) Получаем список узлов (серверов)
    try {
      const response = await getNodes();
      // API может возвращать либо { nodes: [...] }, либо сразу массив
      nodes = response.nodes ?? response;
    } catch (e) {
      console.error("Ошибка при получении списка узлов:", e);
      nodes = [];
    } finally {
      // Сообщаем Svelte, что загрузка завершена
      nodesLoaded = true;
    }

    // 4) Устанавливаем selected_node в сторе
    try {
      const saved = localStorage.getItem("selected_node");
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed?.hostname) {
          selected_node.set(parsed);
        } else if (nodes.length) {
          localStorage.setItem("selected_node", JSON.stringify(nodes[0]));
          selected_node.set(nodes[0]);
        }
      } else if (nodes.length) {
        localStorage.setItem("selected_node", JSON.stringify(nodes[0]));
        selected_node.set(nodes[0]);
      }
    } catch {
      if (nodes.length) {
        localStorage.setItem("selected_node", JSON.stringify(nodes[0]));
        selected_node.set(nodes[0]);
      }
    }
  });
</script>

<NavigationBar />

{#if $is_authorized}
  <div class="mt-16 md:mt-24 z-[9998] px-4">
    {#if nodesLoaded}
      <!-- Когда nodesLoaded === true, сразу рендерим NodeSelector -->
      <NodeSelector {nodes} />
    {:else}
      <!-- Пока nodesLoaded === false, показываем «Загрузка серверов…» -->
      <div class="text-gray-500 dark:text-gray-400 text-sm">
        Загрузка серверов…
      </div>
    {/if}
  </div>

  <!-- Mobile nav (отображается всегда, когда авторизован) -->
  <div class="md:hidden">
    <MobileNav />
  </div>

  <!-- Sidebar (Desktop) -->
  <div class="fixed hidden md:block w-96 h-96 overflow-y-auto">
    <SidebarLayout />
  </div>
{/if}

<!-- Основной контент -->
<div class="md:ml-72">
  {@render children()}
</div>

<style>
  :global(body) {
    background-image: radial-gradient(#ff0000 0.65px, #2bff0000 0.65px);
    background-size: 13px 13px;
  }
</style>
