<script>
  import {
    Pagination,
    P,
    Search,
    Table,
    TableBody,
    TableBodyCell,
    TableBodyRow,
    TableHead,
    TableHeadCell,
    Button,
    Checkbox,
    Tooltip,
    Spinner,
  } from "flowbite-svelte";
  import {
    UserEditOutline,
    LockOutline,
    TrashBinOutline,
    UserAddOutline,
    SearchOutline,
    ChevronLeftOutline,
    ChevronRightOutline,
  } from "flowbite-svelte-icons";
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { getAllUsers } from "$lib/api/users";

  let users = [];
  let searchQuery = "";
  let limit = 2;
  let total = 0;
  let currentPage = 1;
  let pages = [];
  let loading;

  // Получаем текущую страницу и строку поиска из адреса
  $: {
    const params = $page.url.searchParams;
    currentPage = +(params.get("page") || 1);
  }

  // Загружаем пользователей при изменении searchQuery или currentPage
  $: if (currentPage && searchQuery !== "undefined") {
    console.log(currentPage, searchQuery);
    loadUsers();
  }


  async function loadUsers() {
    try {
      loading = true;
      const data = await getAllUsers({
        skip: (currentPage - 1) * limit,
        limit: limit,
        search: searchQuery,
      });
      users = data.users;
      total = data.total;

      const totalPages = Math.ceil(total / limit);
      pages = Array.from({ length: totalPages }, (_, i) => ({
        name: i + 1,
        href: `?page=${i + 1}`,
        active: i + 1 === currentPage,
      }));
      loading = false;
    } catch (err) {
      console.error("Ошибка загрузки пользователей", err);
    }
  }

  function previous() {
    if (currentPage > 1) {
      goto(`?page=${currentPage - 1}`);
    }
  }

  function next() {
    const totalPages = Math.ceil(total / limit);
    if (currentPage < totalPages) {
      goto(`?page=${currentPage + 1}`);
    }
  }
</script>

<div class="flex justify-center mt-6 mb-6">
  <Search
    bind:value={searchQuery}
    maxlength="32"
    class="flex gap-2 items-center"
    placeholder="Поиск по логину..."
  ></Search>
</div>

<Table>
  <TableHead>
    <TableHeadCell>Имя пользователя</TableHeadCell>
    <TableHeadCell>Роли</TableHeadCell>
    <TableHeadCell>Создан</TableHeadCell>
    <TableHeadCell>Действия</TableHeadCell>
  </TableHead>

  <TableBody class="divide-y">
    {#if loading}
      <TableBodyRow>
        <TableBodyCell colspan="4" class="py-8">
          <div class="flex justify-center">
            <Spinner />
          </div>
        </TableBodyCell>
      </TableBodyRow>
    {:else}
      {#each users as user}
        <TableBodyRow>
          <TableBodyCell>{user.username}</TableBodyCell>
          <TableBodyCell>
            {#each user.roles as role}
              <div class="flex items-center space-x-2">
                <Checkbox checked disabled />
                <P>{role.name}</P>
              </div>
            {/each}
          </TableBodyCell>
          <TableBodyCell>{new Date(user.created_at).toLocaleString()}</TableBodyCell>
          <TableBodyCell class="space-x-2">
            <Button size="xs" color="light" on:click={() => alert("Изменить логин")}>
              <UserEditOutline class="w-6 h-6" />
            </Button>
            <Tooltip type="light">Изменить логин</Tooltip>
            <Button size="xs" color="light" on:click={() => alert("Изменить пароль")}>
              <LockOutline class="w-6 h-6" />
            </Button>
            <Tooltip type="light">Изменить пароль</Tooltip>
            <Button outline size="xs" color="red" on:click={() => alert("Удалить пользователя")}>
              <TrashBinOutline class="w-6 h-6" />
            </Button>
            <Tooltip type="light">Удалить пользователя</Tooltip>
          </TableBodyCell>
        </TableBodyRow>
      {/each}
    {/if}
  </TableBody>
</Table>

<div class="flex justify-center mt-4">
  <Pagination {pages} icon on:previous={previous} on:next={next}>
    <svelte:fragment slot="prev">
      <span class="sr-only">Previous</span>
      <ChevronLeftOutline class="w-3.5 h-3.5" />
    </svelte:fragment>

    <svelte:fragment slot="next">
      <span class="sr-only">Next</span>
      <ChevronRightOutline class="w-3.5 h-3.5" />
    </svelte:fragment>
  </Pagination>
</div>

<div class="fixed bottom-4 right-4">
  <Button
    size="xl"
    color="blue"
    class="rounded-full p-3 shadow-lg"
    on:click={() => alert("Добавление пользователя")}
  >
    <UserAddOutline class="w-8 h-8" />
  </Button>
</div>
