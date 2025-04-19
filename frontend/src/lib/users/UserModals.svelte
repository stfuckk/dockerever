<script>
  import { Modal, Label, Input, Button } from "flowbite-svelte";
  import { ExclamationCircleOutline } from "flowbite-svelte-icons";
  import { createEventDispatcher } from "svelte";
  import Toast from "$lib/global/Toast.svelte";
  import { error } from "$lib/stores/authStore";
  import { get } from "svelte/store";

  export let modals;
  export let selectedUser;

  export let onCreate;
  export let onUpdateLogin;
  export let onUpdatePassword;
  export let onDelete;

  const dispatch = createEventDispatcher();

  let newUserLogin = "";
  let newUserPassword = "";
  let newLogin = "";
  let prevPassword = "";
  let newPassword = "";

  let showToast = false;
  let toastMessage = "";

  $: if ($error) {
    toastMessage = $error;
    showToast = true;
    setTimeout(() => {
      showToast = false;
      error.set(null);
    }, 4000);
  }
</script>

{#if showToast}
    <Toast message={toastMessage} />
{/if}

<!-- Создание пользователя -->
<Modal bind:open={modals.create} size="xs" autoclose={false}>
  <form
    class="flex flex-col space-y-6"
    on:submit|preventDefault={async () => {
      try {
        await onCreate({ username: newUserLogin, password: newUserPassword });
        newUserLogin = "";
        newUserPassword = "";
      } catch (e) {
        error.set(e.message);
      }
    }}
  >
    <h3 class="text-xl font-medium text-gray-900 dark:text-white">
      Новый пользователь
    </h3>
    <Label>
      <span>Логин</span>
      <Input bind:value={newUserLogin} placeholder="Логин" required />
    </Label>
    <Label>
      <span>Пароль</span>
      <Input
        bind:value={newUserPassword}
        placeholder="Пароль"
        type="password"
        required
      />
    </Label>
    <Button type="submit">Создать</Button>
  </form>
</Modal>

<!-- Изменение логина -->
<Modal bind:open={modals.editLogin} size="xs" autoclose={false}>
  <form
    class="flex flex-col space-y-6"
    on:submit|preventDefault={async () => {
      try {
        await onUpdateLogin(selectedUser?.id, newLogin, prevPassword);
        newUserLogin = "";
        newUserPassword = "";
      } catch (e) {
        error.set(e.message);
      }
    }}
  >
    <h3 class="text-xl font-medium text-gray-900 dark:text-white">
      Изменение логина пользователя <b>{selectedUser?.username}</b>
    </h3>
    <Label>
      <span>Новый логин</span>
      <Input bind:value={newLogin} placeholder="Новый логин" />
    </Label>
    <Button type="submit">Обновить</Button>
  </form>
</Modal>

<!-- Смена пароля -->
<Modal bind:open={modals.editPassword} size="xs" autoclose={false}>
  <form
    class="flex flex-col space-y-6"
    on:submit|preventDefault={async () => {
      try {
        await onUpdatePassword(
          selectedUser?.id,
          selectedUser?.username,
          newPassword,
          prevPassword
        );
        newUserLogin = "";
        newUserPassword = "";
      } catch (e) {
        error.set(e.message);
      }
    }}
  >
    <h3 class="text-xl font-medium text-gray-900 dark:text-white">
      Смена пароля пользователя <b>{selectedUser?.username}</b>
    </h3>
    <Label>
      <span>Новый пароль</span>
      <Input bind:value={newPassword} type="password" />
    </Label>
    <Button type="submit">Обновить</Button>
  </form>
</Modal>

<!-- Удаление пользователя -->
<Modal bind:open={modals.delete} size="xs" autoclose>
  <div class="text-center">
    <ExclamationCircleOutline
      class="mx-auto mb-4 text-gray-400 w-12 h-12 dark:text-gray-200"
    />
    <h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">
      Удалить пользователя <b>{selectedUser?.username}</b>?
    </h3>
    <Button
      color="red"
      class="me-2"
      on:click={async () => {
        try {
          await onDelete(selectedUser?.id);
        } catch (e) {
          error.set(e.message);
        }
      }}>Удалить</Button
    >
    <Button color="alternative" on:click={() => (modals.delete = false)}
      >Отмена</Button
    >
  </div>
</Modal>
