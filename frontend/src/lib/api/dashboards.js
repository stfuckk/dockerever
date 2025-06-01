// src/lib/api/dashboards.js

import { authFetch } from "./auth";

/**
 * 1) Получить список доступных узлов (node_exporter targets)
 *    GET /api/v1/nodes
 */
export async function getNodes() {
  const res = await authFetch("/api/v1/nodes");
  if (!res.ok) throw new Error("Ошибка при получении узлов");
  return res.json();
}

/**
 * 2) Получить дашборд по title
 *    GET /api/v1/dashboards/title/{title}
 *    Возвращает объект Dashboard со всеми его блоками.
 */
export async function getDashboardByTitle(title) {
  const res = await authFetch(
    `/api/v1/dashboards/title/${encodeURIComponent(title)}`
  );
  if (!res.ok) {
    throw new Error(`Ошибка ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

/**
 * 3) Получить список дашбордов текущего пользователя (или всех, если админ)
 *    GET /api/v1/dashboards
 */
export async function getUserDashboards() {
  const res = await authFetch(`/api/v1/dashboards`);
  if (!res.ok) {
    throw new Error(`Ошибка ${res.status}: ${await res.text()}`);
  }
  return await res.json();
}

/**
 * 4) Создать новый дашборд
 *    POST /api/v1/dashboards
 *    payload = { title, description, system, blocks: [] }
 */
export async function createDashboard(payload) {
  const res = await authFetch(`/api/v1/dashboards`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Ошибка ${res.status}: ${await res.text()}`);
  }
  return await res.json();
}

/**
 * 5) Удалить дашборд
 *    DELETE /api/v1/dashboards/{dashboardId}
 */
export async function deleteDashboard(dashboardId) {
  const res = await authFetch(`/api/v1/dashboards/${dashboardId}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    throw new Error(`Ошибка ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

/**
 * Обновить дашборд (PATCH /api/v1/dashboards/{id})
 */
export async function updateDashboard(id, payload) {
  const res = await authFetch(`/api/v1/dashboards/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Ошибка ${res.status}: ${await res.text()}`);
  }
  return await res.json();
}

/**
 * 6) Создать новый блок внутри дашборда
 *    POST /api/v1/dashboard-blocks/{dashboardId}
 *    payload = { title, type, unit, container_id, metric_type }
 *    (backend сам сгенерит prometheus_query)
 */
export async function createDashboardBlock(dashboardId, payload) {
  const res = await authFetch(`/api/v1/dashboard-blocks/${dashboardId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Ошибка ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

/**
 * 7) Обновить существующий блок дашборда
 *    PATCH /api/v1/dashboard-blocks/{blockId}
 *    payload может содержать { title?, type?, unit?, container_id?, metric_type? }
 *    (backend сам пересчитает prometheus_query)
 */
export async function updateDashboardBlock(blockId, payload) {
  const res = await authFetch(`/api/v1/dashboard-blocks/${blockId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Ошибка ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

/**
 * 8) Удалить блок из дашборда
 *    DELETE /api/v1/dashboard-blocks/{blockId}
 */
export async function deleteDashboardBlock(blockId) {
  const res = await authFetch(`/api/v1/dashboard-blocks/${blockId}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    throw new Error(`Ошибка ${res.status}: ${await res.text()}`);
  }
  return res.json();
}
