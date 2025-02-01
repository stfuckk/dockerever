export async function isUserAuthorized() {
    try {
        const token = localStorage.getItem("token");
        if (token) {
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
            return true;
        }
        else return false;

    } catch (error) {
        console.error('Authorization check failed:', error);
        return false;
    }
}

export async function loginUser(username, password) {
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
            if (errorData.detail === 'Неверный логин или пароль') {
                throw new Error(errorData.detail);
            } else {
                throw new Error('Не удалось подключиться к серверу');
            }
        }
    
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        return data.access_token;
}