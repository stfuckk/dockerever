export async function isUserAuthorized() {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch('/api/auth/token_validate', {
            method: 'GET',
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
        return false;
    }
}

export async function loginUser(username, password) {
    try {
        const body = new URLSearchParams({
            grant_type: 'password',
            username: username,
            password: password,
        });
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: body.toString()
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Error details:', errorData);
            if (errorData.message === 'User not found') {
                throw new Error('Такого пользователя не существует');
            }
            throw new Error('Не удалось подключиться к серверу');
        }

        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        return data.access_token;
    } catch (error) {
        console.error('Login failed:', error);
        throw new Error('Не удалось подключиться к серверу');
    }
}

export async function getUserData() {
    try {
        const token = localStorage.getItem('token');

        const response = await fetch('/api/auth/me', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Error details:', errorData);
            throw new Error('Не удалось получить данные пользователя');
        }

        const userData = await response.json();
        return userData;
    } catch (error) {
        console.error('Failed to retrieve user data:', error);
        throw new Error('Не удалось получить данные пользователя');
    }
}