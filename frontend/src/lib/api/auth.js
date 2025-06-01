import { is_authorized, user } from "$lib/stores/authStore";
import {
  getAccessToken,
  getRefreshToken,
  setTokens,
  clearTokens,
} from "$lib/utils/token";
import { goto } from "$app/navigation";

let isRefreshing = false;
let pendingRequests = [];

/**
 * Обёртка для fetch, которая:
 * 1) Добавляет Authorization: Bearer <access_token>
 * 2) При 401 или invalid_access_token делает refreshToken() и повторяет запрос один раз
 * 3) Если после этого снова 401 — очищает токены и редиректит на /login
 */
export async function authFetch(input, init = {}, retry = true) {
  // Если сейчас идёт refreshToken, ждём его, чтобы взять уже обновлённый токен
  if (isRefreshing) {
    await new Promise((resolve) => pendingRequests.push(resolve));
  }

  const token = getAccessToken();
  const headers = {
    ...(init.headers || {}),
    Authorization: token ? `Bearer ${token}` : "",
  };

  let res;
  try {
    res = await fetch(input, { ...init, headers });
  } catch (networkError) {
    throw new Error("Сетевая ошибка: " + networkError.message);
  }

  // Если сервер вернул OK — сразу отдаём ответ
  if (res.ok) {
    return res;
  }

  // Попробуем прочитать JSON, чтобы найти code === "errors.auth.invalid_access_token"
  let data = null;
  try {
    data = await res.clone().json();
  } catch {
    // не JSON или пусто
  }

  const isInvalidToken =
    res.status === 401 ||
    data?.detail?.code === "errors.auth.invalid_access_token" ||
    data?.detail?.code === "errors.auth.expired_access_token";

  if (isInvalidToken && retry) {
    // Если ещё не обновляем токен, запускаем refresh
    if (!isRefreshing) {
      isRefreshing = true;
      try {
        const refresh_token = getRefreshToken();
        let refreshed = false;

        if (refresh_token) {
          const refreshRes = await fetch("/api/v1/auth/refresh-token", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh_token }),
          });
          if (refreshRes.ok) {
            const newTokens = await refreshRes.json();
            setTokens(newTokens);
            refreshed = true;
          }
        }

        isRefreshing = false;
        // Уведомляем все ожидающие запросы, что refresh завершён
        pendingRequests.forEach((r) => r());
        pendingRequests = [];

        if (refreshed) {
          // Пытаемся получить текущего пользователя и поменять состояние
          try {
            const newUser = await getCurrentUser();
            is_authorized.set(true);
            user.set(newUser);
          } catch {
            // Если даже getCurrentUser не прошёл — оставляем просто обновлённый токен
          }

          // Повторяем исходный запрос один раз (retry=false)
          const newToken = getAccessToken();
          const newHeaders = {
            ...(init.headers || {}),
            Authorization: newToken ? `Bearer ${newToken}` : "",
          };
          const retryRes = await fetch(input, { ...init, headers: newHeaders });
          if (retryRes.ok) {
            return retryRes;
          }
        }
      } catch {
        // Ошибка при попытке refreshToken()
        isRefreshing = false;
        pendingRequests.forEach((r) => r());
        pendingRequests = [];
      }
    } else {
      // Если refresh уже в процессе, подождём завершения, а затем повторим authFetch
      await new Promise((resolve) => pendingRequests.push(resolve));
      return authFetch(input, init, false);
    }

    // Если мы оказались здесь, значит refresh не помог или повторный запрос вернул не OK
    clearTokens();
    is_authorized.set(false);
    goto("/login");
    throw new Error("Сессия истекла, требуется вход заново.");
  }

  // Во всех остальных случаях возвращаем текст ошибки
  const errorText = data?.detail?.ruText || `Ошибка ${res.status}`;
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
