
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
  