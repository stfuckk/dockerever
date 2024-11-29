<script>
    import { page } from '$app/stores';
    import { Img, Card } from 'flowbite-svelte';
</script>

<div class="flex justify-center mt-4">
    {#if $page.status=='404' }
    <Card horizontal size="md" class="text-center">
        <Img src="error.png" alt="Error Image" draggable="false" class="w-32 h-32 mx-auto my-auto select-none" />
        <div class="flex flex-col">
            <h5 class="text-2xl font-bold tracking-tight text-gray-900 dark:text-white mx-auto my-auto">Ошибка: {$page.status}: {$page.error.message}</h5>
            <p class="text-md tracking-tight text-gray-900 dark:text-white mx-auto my-auto">Страница не найдена или находится в разработке</p>
        </div>
    </Card>
    {/if}
</div>