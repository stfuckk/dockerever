import { writable } from 'svelte/store';

// объект узла: { ip, hostname }
export const selected_node = writable(null);
