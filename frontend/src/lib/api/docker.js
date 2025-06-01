// src/lib/api/docker.js
import { authFetch } from "./auth";

/**
 * Получить список контейнеров. По умолчанию search = ""
 * Backend-роут: GET /api/v1/docker/containers?search=…
 * Возвращает JSON вида { containers: [ { id, name, status, image }, … ] }
 */
export async function getContainers(search = "") {
  const params = new URLSearchParams();
  if (search) {
    params.append("search", search);
  }
  const queryString = params.toString() ? `?${params.toString()}` : "";
  const res = await authFetch(`/api/v1/docker/containers${queryString}`);
  if (!res.ok) {
    throw new Error(`Ошибка ${res.status}: ${await res.text()}`);
  }
  return res.json();
}
