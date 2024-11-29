export async function isUserAuthorized(token) {
    try {
        const response = await fetch('/api/check-token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            return false;
        }

        const data = await response.json();
        return data.status;
    } catch (error) {
        console.error('Authorization check failed:', error);
        return true;
    }
}

export async function loginUser(username, password) {
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            const errorData = await response.json();
            if (errorData.message === 'User not found') {
                throw new Error('Такого пользователя не существует');
            }
            throw new Error('Не удалось подключиться к серверу');
        }

        const data = await response.json();
        localStorage.setItem('token', data.token);
        return data.token;
    } catch (error) {
        console.error('Login failed:', error);
        throw new Error('Не удалось подключиться к серверу');
    }
}