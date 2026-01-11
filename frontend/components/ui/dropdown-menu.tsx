'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

interface DropdownMenuContextType {
  close: () => void;
}

const DropdownMenuContext = React.createContext<DropdownMenuContextType | null>(null);

interface DropdownMenuProps {
  children: React.ReactNode;
  trigger: React.ReactNode;
  className?: string;
}

export function DropdownMenu({ children, trigger, className }: DropdownMenuProps) {
  const [open, setOpen] = React.useState(false);
  const menuRef = React.useRef<HTMLDivElement>(null);

  const close = React.useCallback(() => {
    setOpen(false);
  }, []);

  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }

    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [open]);

  return (
    <DropdownMenuContext.Provider value={{ close }}>
      <div className="relative" ref={menuRef}>
        <div onClick={() => setOpen(!open)}>{trigger}</div>
        {open && (
          <div
            className={cn(
              'absolute right-0 mt-2 w-48 rounded-md border bg-popover shadow-lg z-50',
              className
            )}
          >
            {children}
          </div>
        )}
      </div>
    </DropdownMenuContext.Provider>
  );
}

interface DropdownMenuItemProps {
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
}

export function DropdownMenuItem({ children, onClick, className }: DropdownMenuItemProps) {
  const context = React.useContext(DropdownMenuContext);

  const handleClick = () => {
    onClick?.();
    context?.close();
  };

  return (
    <div
      className={cn(
        'px-4 py-2 text-sm cursor-pointer hover:bg-accent hover:text-accent-foreground transition-colors first:rounded-t-md last:rounded-b-md',
        className
      )}
      onClick={handleClick}
    >
      {children}
    </div>
  );
}

