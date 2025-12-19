'use client';

import { FormEvent, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useLoginMutation, useMeQuery } from '@/lib/api';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [login, { isLoading, error }] = useLoginMutation();
  const { data: user } = useMeQuery();

  // Redirect if already logged in
  useEffect(() => {
    if (user) {
      router.push('/');
    }
  }, [user, router]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const result = await login({ email, password }).unwrap();
      localStorage.setItem('access_token', result.access_token);
      router.push('/');
    } catch (err) {
      console.error('Login failed', err);
    }
  };

  // Show loading or nothing while checking auth
  if (user) {
    return null;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md border rounded-xl p-6 shadow-sm bg-card">
        <h1 className="text-xl font-semibold mb-4 text-center">Sign in</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-medium" htmlFor="email">
              Email
            </label>
            <Input
              id="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium" htmlFor="password">
              Password
            </label>
            <Input
              id="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && (
            <p className="text-xs text-destructive">
              Failed to sign in. Check your credentials and try again.
            </p>
          )}
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? 'Signing in...' : 'Sign in'}
          </Button>
        </form>

        <p className="mt-4 text-center text-xs text-muted-foreground">
          Don&apos;t have an account?{' '}
          <button
            type="button"
            className="text-primary hover:underline"
            onClick={() => router.push('/signup')}
          >
            Sign up
          </button>
        </p>
      </div>
    </div>
  );
}



