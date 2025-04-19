
export function getAccessToken() {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('access_token');
}
  
export function getRefreshToken() {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('refresh_token');
}
  
export function setTokens({ access_token, refresh_token }) {
    if (typeof window === 'undefined' || !access_token || !refresh_token) return;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
  }
  
export function clearTokens() {
    if (typeof window === 'undefined') return;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

export async function waitForToken(timeout = 3000) {
    const interval = 50;
    let waited = 0;
    while (typeof window !== 'undefined' && !localStorage.getItem('access_token')) {
      await new Promise((r) => setTimeout(r, interval));
      waited += interval;
      if (waited >= timeout) break;
    }
  }
  
  