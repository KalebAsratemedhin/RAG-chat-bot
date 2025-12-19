'use client';

import { FormEvent, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useSignupMutation, useMeQuery } from '@/lib/api';

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [signup, { isLoading, error }] = useSignupMutation();
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
      const result = await signup({ email, password }).unwrap();
      // Store the token (if signup now returns a token)
      if (result.access_token) {
        localStorage.setItem('access_token', result.access_token);
        router.push('/');
      } else {
        // Fallback: redirect to login if token not returned
        router.push('/login');
      }
    } catch (err: any) {
      console.error('Signup failed', err);
      if (err?.data) {
        console.error('Error details:', err.data);
      }
    }
  };

  // Show loading or nothing while checking auth
  if (user) {
    return null;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md border rounded-xl p-6 shadow-sm bg-card">
        <h1 className="text-xl font-semibold mb-4 text-center">
          Create an account
        </h1>
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
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && (
            <p className="text-xs text-destructive">
              Failed to sign up. This email might already be registered.
            </p>
          )}
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? 'Creating account...' : 'Sign up'}
          </Button>
        </form>

        <p className="mt-4 text-center text-xs text-muted-foreground">
          Already have an account?{' '}
          <button
            type="button"
            className="text-primary hover:underline"
            onClick={() => router.push('/login')}
          >
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
}



