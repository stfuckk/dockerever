import { is_authorized, user } from "$lib/stores/authStore";
import {
  getAccessToken,
  getRefreshToken,
  setTokens,
  clearTokens,
} from "$lib/utils/token";

let isRefreshing = false;

export async function authFetch(input, init = {}, retry = true) {
  const token = getAccessToken();
  const headers = {
    ...(init.headers || {}),
    Authorization: `Bearer ${token}`,
  };

  const res = await fetch(input, {
    ...init,
    headers,
  });

  if (res.ok) return res;

  let data = null;
  try {
    data = await res.clone().json(); // чтобы можно было прочитать тело повторно
  } catch {}

  const isInvalidToken =
    data?.detail?.code === "errors.auth.invalid_access_token";

  if (isInvalidToken && retry && !isRefreshing) {
    isRefreshing = true;
    const refreshed = await refreshToken();
    isRefreshing = false;

    if (refreshed) {
      try {
        const newUser = await getCurrentUser();
        is_authorized.set(true);
        user.set(newUser);
        return await authFetch(input, init, false); // повторяем только один раз
      } catch {
        console.log("Ошибка при получении пользователя");
      }
    }
  }

  const errorText = data?.detail?.ruText || "Ошибка запроса";
  throw new Error(errorText);
}

export async function getCurrentUser() {
  const token = getAccessToken();
  if (!token) throw new Error("Необходимо войти");

  const res = await fetch("/api/v1/auth/test-token", {
    method: "POST",
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (res.ok) {
    return await res.json();
  } else {
    const err = await res.json();

    if (err.detail.code === "errors.auth.must_change_password") {
      return {
        must_change_password: true,
        username: err.data?.username ?? "unknown",
      };
    }

    throw new Error(err.detail.ruText);
  }
}

export async function refreshToken() {
  const refresh_token = getRefreshToken();
  if (!refresh_token) return null;

  const res = await fetch("/api/v1/auth/refresh-token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token }),
  });

  if (!res.ok) return false;

  const data = await res.json();
  setTokens(data);
  return true;
}

export async function refreshTokenAndUser() {
  const refreshed = await refreshToken();
  if (!refreshed) return null;

  try {
    const userData = await getCurrentUser();
    is_authorized.set(true);
    user.set(userData);
    return userData;
  } catch {
    console.log("Не удалось обновить токен.");
    await refreshTokenAndUser();
    return null;
  }
}

export async function isAuthorized() {
  try {
    return await getCurrentUser();
  } catch (err) {
    const isExpired =
      err.message.includes("401") ||
      err.message.includes("Неверный access token");

    if (isExpired) {
      const userData = await refreshTokenAndUser();
      return userData;
    }

    console.log("Не удалось получить пользователя:", err);
    return null;
  }
}

export async function loginUser({ username, password }) {
  const form = new URLSearchParams();
  form.append("username", username);
  form.append("password", password);

  const res = await authFetch("/api/v1/auth/access-token", {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail.ruText);
  }

  const data = await res.json();
  setTokens(data);

  const checkRes = await fetch("/api/v1/auth/test-token", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${data.access_token}`,
    },
  });

  if (checkRes.ok) {
    const userData = await checkRes.json();
    is_authorized.set(true);
    user.set(userData);

    return {
      ...data,
      must_change_password: false,
      username: userData.username,
    };
  } else {
    const err = await checkRes.json();
    if (err.detail.code === "errors.auth.must_change_password") {
      return {
        access_token: data.access_token,
        must_change_password: true,
        username: err.data?.username ?? "unknown",
      };
    }

    throw new Error(err.detail.ruText);
  }
}

export async function changePassword(data, token) {
  const res = await authFetch("/api/v1/users/me", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  if (res.ok) {
    return true;
  } else {
    const err = await res.json();
    throw new Error(err.detail.ruText || "Ошибка при смене пароля");
  }
}

export async function updateUsername(data, token) {
  const res = await authFetch("/api/v1/users/me", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err?.ruText || "Ошибка при обновлении логина");
  }
  return await res.json();
}
