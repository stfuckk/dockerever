import { authFetch } from "$lib/api/auth";

/** ==== IMAGES ==== */
export async function getImages() {
  const res = await authFetch("/api/v1/docker_ext/images");
  if (!res.ok) throw new Error("Ошибка при получении списка образов");
  return await res.json();
}

export async function deleteImage(imageId) {
  const res = await authFetch(`/api/v1/docker_ext/images/${imageId}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Ошибка при удалении образа");
  }
  return true;
}

/** ==== NETWORKS ==== */
export async function getNetworks() {
  const res = await authFetch("/api/v1/docker_ext/networks");
  if (!res.ok) throw new Error("Ошибка при получении списка сетей");
  return await res.json();
}

export async function deleteNetwork(networkId) {
  const res = await authFetch(`/api/v1/docker_ext/networks/${networkId}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Ошибка при удалении сети");
  }
  return true;
}

export async function getNetworkContainers(networkId) {
  const res = await authFetch(
    `/api/v1/docker_ext/networks/${networkId}/containers`
  );
  if (!res.ok) throw new Error("Ошибка при получении контейнеров сети");
  return await res.json(); // { containers: [...] }
}

/** ==== VOLUMES ==== */
export async function getVolumes() {
  const res = await authFetch("/api/v1/docker_ext/volumes");
  if (!res.ok) throw new Error("Ошибка при получении списка томов");
  return await res.json();
}

export async function deleteVolume(volumeName) {
  const res = await authFetch(`/api/v1/docker_ext/volumes/${volumeName}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Ошибка при удалении тома");
  }
  return true;
}
