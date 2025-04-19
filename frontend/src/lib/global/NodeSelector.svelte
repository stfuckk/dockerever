<script>
    import { Select } from 'flowbite-svelte';
  
    export let selectedNode = '';
    export let nodes = [];
  </script>
  
  <div class="px-2 mb-12 dark:bg-gray-800">
    <Select
      class="mt-2 text-gray-900 dark:text-white bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 focus:ring-blue-500 dark:focus:ring-blue-500 focus:border-blue-500 dark:focus:border-blue-500"
      items={nodes.map((n) => ({ value: n, name: n }))}
      placeholder="Выбор сервера"
      bind:value={selectedNode}
    />
  </div>
  