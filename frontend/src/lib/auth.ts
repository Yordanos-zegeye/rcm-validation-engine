export const auth = {
  getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('token');
  },
  setToken(token: string) {
    if (typeof window === 'undefined') return;
    localStorage.setItem('token', token);
    document.cookie = `token=${token}; path=/`;
  },
  clear() {
    if (typeof window === 'undefined') return;
    localStorage.removeItem('token');
    localStorage.removeItem('refresh');
    document.cookie = 'token=; Max-Age=0; path=/';
  },
  getTenant(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('tenantId');
  },
  setTenant(id: string) {
    if (typeof window === 'undefined') return;
    localStorage.setItem('tenantId', id);
  }
}
