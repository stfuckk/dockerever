<script>
  import AuthForm from "$lib/users/AuthForm.svelte";
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { is_authorized, user } from "$lib/stores/authStore";
  import Toast from "$lib/global/Toast.svelte";
  import { page } from "$app/stores";
  import { isAuthorized } from "$lib/api/auth";

  let showToast = false;
  const animatedText = "Dockerever";
  const letters = animatedText.split("");

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

<div class="w-full max-w-md order-2 md:order-1 relative z-10">
  <AuthForm />
</div>
<div
  class="z-0 absolute inset-0 overflow-hidden top-48 flex justify-center items-center"
>
  <div class="whitespace-nowrap">
    {#each letters as letter, index}
      <span
        class="inline-block select-none text-[clamp(16vw,10vw,12vw)] font-extrabold text-gray-900 dark:text-white leading-none"
        style="animation-delay: {index * 0.1}s"
      >
        {letter}
      </span>
    {/each}
  </div>
</div>

<style>
  @keyframes jump {
    0% {
      transform: translateY(0);
    }
    30% {
      transform: translateY(-0.3em);
    }
    50% {
      transform: translateY(0);
    }
    70% {
      transform: translateY(-0.15em);
    }
    100% {
      transform: translateY(0);
    }
  }
  span {
    animation: jump 1.2s ease-in-out infinite;
  }
</style>
