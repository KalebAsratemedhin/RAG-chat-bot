'use client';

import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { Button } from '@/components/ui/button';
import { LogOut, MessageSquare, HelpCircle } from 'lucide-react';

export function ChatHeader() {
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    router.push('/login');
  };

  return (
    <header className="sticky top-0 z-20 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center px-4 justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-semibold">RAG Chat Bot</h1>
          <nav className="flex items-center gap-2">
            <Link href="/">
              <Button
                variant={pathname === '/' ? 'default' : 'ghost'}
                size="sm"
              >
                <MessageSquare className="h-4 w-4 mr-2" />
                Chat
              </Button>
            </Link>
            <Link href="/questions">
              <Button
                variant={pathname?.startsWith('/questions') ? 'default' : 'ghost'}
                size="sm"
              >
                <HelpCircle className="h-4 w-4 mr-2" />
                Q&A
              </Button>
            </Link>
          </nav>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Button variant="ghost" size="icon" onClick={handleLogout} title="Logout">
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}