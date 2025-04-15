import { getAccessToken } from "$lib/utils/token";
import { authFetch } from "$lib/api/auth";

const BASE_URL = '/api/v1/users';

export async function getAllUsers({ skip = 0, limit = 10, search='' } = {}) {
	const res = await authFetch(`${BASE_URL}?skip=${skip}&limit=${limit}&search=${search}`);
	if (!res.ok) throw new Error('Ошибка при получении пользователей');
	return await res.json();
}

export async function createUser(data) {
    const res = await authFetch(`${BASE_URL}`, {
        method: 'POST',
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err?.ruText || 'Ошибка при создании пользователя');
    }
    return await res.json()
}

export async function updateUser(userId, data) {
	const res = await authFetch(`${BASE_URL}/${userId}`, {
		method: 'PUT',
		body: JSON.stringify(data),
	});
	if (!res.ok) {
		const err = await res.json();
		throw new Error(err?.ruText || 'Ошибка при обновлении пользователя');
	}
	return await res.json();
}

export async function deleteUser(userId) {
	const res = await authFetch(`${BASE_URL}/${userId}`, {
		method: 'DELETE',
	});
	if (!res.ok) {
		const err = await res.json();
		throw new Error(err?.ruText || 'Ошибка при удалении пользователя');
	}
	return await res.json();
}

export async function assignUserRole(userId, roleName) {
	const res = await authFetch(`/api/v1/user-roles/${userId}`, {
		method: 'POST',
		body: JSON.stringify({ role_name: roleName }),
	});
	if (!res.ok) {
		const err = await res.json();
		throw new Error(err?.ruText || 'Ошибка при назначении роли');
	}
	return await res.json();
}

export async function removeUserRole(userId, roleName) {
	const res = await authFetch(`/api/v1/user-roles/${userId}`, {
		method: 'DELETE',
		body: JSON.stringify({ role_name: roleName }),
	});
	if (!res.ok) {
		const err = await res.json();
		throw new Error(err?.ruText || 'Ошибка при удалении роли');
	}
	return await res.json();
}