import { writable } from 'svelte/store';

export const is_authorized = writable(false);
export const user = writable(null);
export const error = writable(null);