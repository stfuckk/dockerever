<script>
  import { onMount } from "svelte";
  import {
    getCurrentUser,
    updateUsername,
    changePassword,
  } from "$lib/api/auth";
  import { user, error } from "$lib/stores/authStore";
  import { get } from "svelte/store";
  import {
    Accordion,
    AccordionItem,
    Card,
    Label,
    Input,
    Button,
    Helper,
  } from "flowbite-svelte";
  import { getAccessToken } from "$lib/utils/token";
  import { EyeOutline, EyeSlashOutline } from "flowbite-svelte-icons";

  let show1 = false;
  let show2 = false;
  let show3 = false;
  let currentUser = get(user);
  let newUsername = "";
  let prevPassword = "";
  let newPassword = "";
  let updateError = "";
  let successMessage = "";

  onMount(async () => {
    try {
      currentUser = await getCurrentUser();
      user.set(currentUser);
    } catch (err) {
      error.set(err.message);
    }
  });

  async function handleChangeUsername(event) {
    event.preventDefault();
    updateError = "";
    successMessage = "";
    try {
      await updateUsername(
        { username: newUsername, prev_password: prevPassword },
        getAccessToken()
      );
      successMessage = "Логин успешно обновлён";
      currentUser.username = newUsername;
      user.set(currentUser);
      newUsername = "";
      newPassword = "";
      prevPassword = "";
    } catch (err) {
      updateError = err.message;
    }
  }

  async function handleChangePassword(event) {
    event.preventDefault();
    updateError = "";
    successMessage = "";
    try {
      await changePassword(
        {
          username: currentUser.username,
          password: newPassword,
          prev_password: prevPassword,
        },
        getAccessToken()
      );
      successMessage = "Пароль успешно обновлён";
      prevPassword = "";
      newPassword = "";
    } catch (err) {
      updateError = err.message;
    }
  }
</script>

<div class="flex mt-8 px-4">
  <Card class="w-full max-w-2xl">
    <h3 class="text-xl font-semibold dark:text-white">Профиль</h3>
    <p class="dark:text-white">
      <strong>Имя пользователя:</strong>
      {currentUser?.username}
    </p>
    <p class="dark:text-white">
      <strong>Роли:</strong>
      {currentUser?.roles.map((r) => r.name).join(" | ")}
    </p>

    <Accordion flush class="mt-6">
      <AccordionItem>
        <span slot="header" class="dark:text-white">Сменить логин</span>
        <div class="space-y-4">
          <Label>
            Текущий пароль
            <Input
              class="mt-2"
              type={show1 ? "text" : "password"}
              bind:value={prevPassword}
              placeholder="•••••••••"
              required
            >
              <button
                slot="right"
                on:click={() => (show1 = !show1)}
                class="pointer-events-auto"
              >
                {#if show1}
                  <EyeOutline class="w-6 h-6" />
                {:else}
                  <EyeSlashOutline class="w-6 h-6" />
                {/if}
              </button>
            </Input>
          </Label>
          <Label>
            Новый логин
            <Input
              class="mt-2"
              bind:value={newUsername}
              placeholder="Введите новый логин"
            />
          </Label>
          <Button on:click={handleChangeUsername}>Обновить логин</Button>
        </div>
      </AccordionItem>

      <AccordionItem>
        <span slot="header" class="dark:text-white">Сменить пароль</span>
        <div class="space-y-4">
          <Label>
            Текущий пароль
            <Input
              class="mt-2"
              type={show2 ? "text" : "password"}
              bind:value={prevPassword}
              placeholder="•••••••••"
              required
            >
              <button
                slot="right"
                on:click={() => (show2 = !show2)}
                class="pointer-events-auto"
              >
                {#if show2}
                  <EyeOutline class="w-6 h-6" />
                {:else}
                  <EyeSlashOutline class="w-6 h-6" />
                {/if}
              </button>
            </Input>
          </Label>
          <Label>
            Новый пароль
            <Input
              class="mt-2"
              type={show3 ? "text" : "password"}
              bind:value={newPassword}
              placeholder="•••••••••"
              required
            >
              <button
                slot="right"
                on:click={() => (show3 = !show3)}
                class="pointer-events-auto"
              >
                {#if show3}
                  <EyeOutline class="w-6 h-6" />
                {:else}
                  <EyeSlashOutline class="w-6 h-6" />
                {/if}
              </button>
            </Input>
          </Label>
          <Button on:click={handleChangePassword}>Обновить пароль</Button>
        </div>
      </AccordionItem>
    </Accordion>

    {#if updateError}
      <Helper class="mt-4" color="red">{updateError}</Helper>
    {/if}
    {#if successMessage}
      <Helper class="mt-4" color="green">{successMessage}</Helper>
    {/if}
  </Card>
</div>
