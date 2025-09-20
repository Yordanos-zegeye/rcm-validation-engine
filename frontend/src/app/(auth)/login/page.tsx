"use client";
import { useState } from 'react';
import api from '@/lib/api';
import { useRouter } from 'next/navigation';
import { auth } from '@/lib/auth';

export default function LoginPage() {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin');
  const [tenant, setTenant] = useState('1');
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const r = await api.post('/auth/token/', { username, password });
  auth.setToken(r.data.access);
  auth.setTenant(tenant);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: 420, margin: '80px auto' }}>
        <h2>Login</h2>
        <form onSubmit={onSubmit} className="grid">
          <input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
          <input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <input placeholder="Tenant ID" value={tenant} onChange={(e) => setTenant(e.target.value)} />
          {error && <div className="badge red">{error}</div>}
          <button type="submit">Sign in</button>
        </form>
      </div>
    </div>
  );
}
