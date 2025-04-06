import { is_authorized, user } from '$lib/stores/authStore';
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from '$lib/utils/token';

export async function getCurrentUser() {
  const token = getAccessToken();
  if (!token) throw new Error('Нет токена');

  const res = await fetch('/api/v1/auth/test-token', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  });

  if (res.ok) {
    return await res.json();
  } else {
    const err = await res.json();

    if (err.detail.code === 'errors.auth.must_change_password') {
        return {must_change_password: true, username: err.data?.username ?? 'unknown'};
    }

    throw new Error(err.detail.ruText);
  }
}

export async function refreshToken() {
  const refresh_token = getRefreshToken();
  if (!refresh_token) return false;

  const res = await fetch('/api/v1/auth/refresh-token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token })
  });

  if (!res.ok) return false;

  const data = await res.json();
  setTokens(data);
  return true;
}

export async function isAuthorized() {
  try {
    return await getCurrentUser();
  } catch (err) {
    if (err.message.includes('401')) {
      const refreshed = await refreshToken();
      if (refreshed) return await getCurrentUser();
    }
    clearTokens();

    is_authorized.set(false);
    user.set(null);
    return null;
  }
}

export async function loginUser({ username, password }) {
  const form = new URLSearchParams();
  form.append('username', username);
  form.append('password', password);

  const res = await fetch('/api/v1/auth/access-token', {
    method: 'POST',
    body: form
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail.ruText);
  }

  const data = await res.json();
  setTokens(data);

  const checkRes = await fetch('/api/v1/auth/test-token', {
    method: 'POST',
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
        username: userData.username
    }
  } else {
    const err = await checkRes.json();
    if (err.detail.code === 'errors.auth.must_change_password') {
        return {
            access_token: data.access_token,
            must_change_password: true,
            username: err.data?.username ?? 'unknown'
        };
    }

    throw new Error(err.detail.ruText);
  }
}

export async function changePassword(data, token) {
  const res = await fetch('/api/v1/users/me', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  });

  if (res.ok) {
    return true;
  } else {
    const err = await res.json();
    throw new Error(err.detail.ruText || 'Ошибка при смене пароля');
  }
}
