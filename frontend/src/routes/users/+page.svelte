<script>
  import {
    Pagination,
    Search,
    Table,
    TableBody,
    TableBodyCell,
    TableBodyRow,
    TableHead,
    TableHeadCell,
    Button,
    Spinner,
    Tooltip,
  } from "flowbite-svelte";
  import {
    UserEditOutline,
    LockOutline,
    TrashBinOutline,
    UserAddOutline,
    ChevronLeftOutline,
    ChevronRightOutline,
  } from "flowbite-svelte-icons";

  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import {
    getAllUsers,
    getAllRoles,
    createUser,
    updateUser,
    deleteUser,
  } from "$lib/api/users";
  import { user as userStore } from "$lib/stores/authStore";
  import { get, derived } from "svelte/store";
  import { onMount } from "svelte";
  import { error } from "$lib/stores/authStore";
  import UserRoleCheckboxes from "$lib/users/UserRoleCheckboxes.svelte";
  import UserModals from "$lib/users/UserModals.svelte";

  let users = [];
  let roles = [];
  let total = 0;
  let loading = true;
  const limit = 5;

  let currentPage = 1;
  let searchInput = "";

  const pageIndex = derived(
    page,
    ($page) => +$page.url.searchParams.get("page") || 1
  );
  const queryText = derived(
    page,
    ($page) => $page.url.searchParams.get("search") || ""
  );

  let selectedUser = null;
  let modals = {
    create: false,
    editLogin: false,
    editPassword: false,
    delete: false,
  };

  onMount(() => {
    const unsub1 = pageIndex.subscribe((val) => {
      currentPage = val;
      loadUsers();
    });

    const unsub2 = queryText.subscribe((val) => {
      searchInput = val;
      loadUsers();
    });

    return () => {
      unsub1();
      unsub2();
    };
  });

  async function loadUsers() {
    try {
      loading = true;
      const data = await getAllUsers({
        skip: (currentPage - 1) * limit,
        limit,
        search: searchInput,
      });

      users = data.users;
      total = data.total;

      roles = await getAllRoles();
    } catch (err) {
      console.error("Ошибка загрузки пользователей", err);
    } finally {
      loading = false;
    }
  }

  function previous() {
    if (currentPage > 1) {
      goto(`?page=${currentPage - 1}&search=${searchInput}`);
    }
  }

  function next() {
    const totalPages = Math.ceil(total / limit);
    if (currentPage < totalPages) {
      goto(`?page=${currentPage + 1}&search=${searchInput}`);
    }
  }

  function search() {
    goto(`?page=1&search=${searchInput}`);
  }

  $: pages = Array.from({ length: Math.ceil(total / limit) }, (_, i) => ({
    name: i + 1,
    href: `?page=${i + 1}&search=${searchInput}`,
    active: i + 1 === currentPage,
  }));

  async function handleCreateUser(data) {
    try {
      await createUser(data);
      modals.create = false;
      await loadUsers();
    } catch (e) {
      error.set(e.message);
    }
  }

  async function handleUpdateLogin(userId, newLogin, prevPassword) {
    try {
      await updateUser(userId, {
        username: newLogin,
        prev_password: "temp1",
      });
      modals.editLogin = false;
      await loadUsers();
    } catch (e) {
      error.set(e.message);
    }
  }

  async function handleUpdatePassword(
    userId,
    newLogin,
    newPassword,
    prevPassword
  ) {
    try {
      await updateUser(userId, {
        username: newLogin,
        password: newPassword,
        prev_password: "temp1",
      });
      modals.editPassword = false;
    } catch (e) {
      error.set(e.message);
    }
  }

  async function handleDeleteUser(userId) {
    try {
      await deleteUser(userId);
      modals.delete = false;
      await loadUsers();
    } catch (e) {
      error.set(e.message);
    }
  }
</script>

<div class="flex w-full max-w-6xl mx-auto mt-32 mb-4 px-4 z-10">
  <Search
    bind:value={searchInput}
    maxlength="32"
    class="flex gap-2 items-center"
    placeholder="Поиск по логину..."
    on:keydown={(e) => e.key === "Enter" && search()}
  />
</div>

<div class="w-full max-w-6xl mx-auto px-4 mt-4 z-10">
  <Table>
    <TableHead>
      <TableHeadCell>Имя пользователя</TableHeadCell>
      <TableHeadCell>Роли</TableHeadCell>
      <TableHeadCell>Создан</TableHeadCell>
      <TableHeadCell>Действия</TableHeadCell>
    </TableHead>

    <TableBody class="divide-y">
      {#if loading || !get(userStore)}
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
            <TableBodyCell>
              {user.username}
              {#if user.username === get(userStore).username}(Вы){/if}
            </TableBodyCell>
            <TableBodyCell>
              <UserRoleCheckboxes {user} {roles} />
            </TableBodyCell>
            <TableBodyCell>
              {new Date(user.created_at).toLocaleString()}
            </TableBodyCell>
            <TableBodyCell class="space-x-2">
              <Button
                size="xs"
                color="light"
                on:click={() => {
                  selectedUser = user;
                  modals.editLogin = true;
                }}
                disabled={user.username === get(userStore).username}
              >
                <UserEditOutline class="w-6 h-6" />
              </Button>
              <Tooltip type="light">Изменить логин</Tooltip>

              <Button
                size="xs"
                color="light"
                on:click={() => {
                  selectedUser = user;
                  modals.editPassword = true;
                }}
                disabled={user.username === get(userStore).username}
              >
                <LockOutline class="w-6 h-6" />
              </Button>
              <Tooltip type="light">Изменить пароль</Tooltip>

              <Button
                outline
                size="xs"
                color="red"
                on:click={() => {
                  selectedUser = user;
                  modals.delete = true;
                }}
                disabled={user.username === get(userStore).username}
              >
                <TrashBinOutline class="w-6 h-6" />
              </Button>
              <Tooltip type="light">Удалить пользователя</Tooltip>
            </TableBodyCell>
          </TableBodyRow>
        {/each}
      {/if}
    </TableBody>
  </Table>
</div>
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

<!-- Кнопка добавления пользователя -->
<div class="fixed bottom-4 right-4 mb-16">
  <Button
    size="xl"
    color="blue"
    class="rounded-full p-3 shadow-lg"
    on:click={() => (modals.create = true)}
  >
    <UserAddOutline class="w-8 h-8" />
  </Button>
</div>

<!-- Компонент с модалками -->
<UserModals
  bind:modals
  bind:selectedUser
  on:refresh={loadUsers}
  onCreate={handleCreateUser}
  onUpdateLogin={handleUpdateLogin}
  onUpdatePassword={handleUpdatePassword}
  onDelete={handleDeleteUser}
/>
