import { authFetch } from "./auth";

/**
 * Промежуточный Range-запрос к /prometheus/range
 * @param {string} query   PromQL выражение
 * @param {string} instance IP:port или hostname
 * @param {number} start   Unix секунда
 * @param {number} end     Unix секунда
 * @param {number} step    шаг в секундах
 */
export async function getPrometheusRange(query, instance, start, end, step) {
  const params = new URLSearchParams({ query });
  if (instance) params.append("instance", instance);
  params.append("start", String(start));
  params.append("end", String(end));
  params.append("step", String(step));
  const res = await authFetch(`/api/v1/prometheus/range?${params}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
/**
 * Мгновенный запрос к /prometheus
 * @param {string} query
 * @param {string} instance
 */
export async function getPrometheusQuery(query, instance) {
  const params = new URLSearchParams({ query });
  if (instance) params.append("instance", instance);

  const res = await authFetch(`/api/v1/prometheus?${params.toString()}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
