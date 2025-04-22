import { authFetch } from "$lib/api/auth";

export async function getNodes() {
  const res = await authFetch("/api/v1/nodes");
  if (!res.ok) throw new Error("Ошибка при получении пользователей");
  return await res.json();
}
