<script>
  import AuthForm from "$lib/users/AuthForm.svelte";
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { is_authorized, user } from "$lib/stores/authStore";
  import Toast from "$lib/global/Toast.svelte";
  import { get } from "svelte/store";
  import { page } from "$app/stores";
  import { isAuthorized } from "$lib/api/auth";

  let showToast = false;

  onMount(async () => {
    const url = $page.url;
    if (url.searchParams.get("reason") === "must_change_password") {
      showToast = true;
    }
    const currentUser = await isAuthorized();
    if (currentUser) {
      is_authorized.set(true);
      user.set(currentUser);
      if (!currentUser.must_change_password) {
        goto("/");
      }
    }
  });
</script>

{#if showToast}
  <Toast message="Вы должны сменить пароль перед использованием системы." />
{/if}
<!-- Форма логина -->
<div class="flex">
  <AuthForm />
  <div class="gooey fixed z-[-1] ml-32"></div>
</div>
