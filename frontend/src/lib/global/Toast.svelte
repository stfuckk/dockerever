<script>
    import { Toast } from 'flowbite-svelte';
    import { CloseCircleSolid } from 'flowbite-svelte-icons';
    import { fly } from 'svelte/transition';

    export let message = '';
</script>
  
<Toast transition={fly} param={{x:200}} color="red" class="mb-4 z-[9999]" position="bottom-right">
    <svelte:fragment slot="icon">
        <CloseCircleSolid class="w-5 h-5" />
        <span class="sr-only">Error icon</span>
    </svelte:fragment>
    {message}
</Toast>
