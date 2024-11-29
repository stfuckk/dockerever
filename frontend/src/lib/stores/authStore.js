import { writable } from 'svelte/store';

export const isAuthorized = writable(false);
export const error = writable(null);
export const userData = writable(null);