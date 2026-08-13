'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { 
  LayoutDashboard, 
  Target, 
  BarChart3, 
  Dna, 
  Sparkles, 
  History, 
  Shield, 
  Compass
} from 'lucide-react';

const NAV_ITEMS = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Focus Session', href: '/focus', icon: Target },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'FocusDNA Profile', href: '/focusdna', icon: Dna },
  { name: 'AI Insights', href: '/insights', icon: Sparkles },
  { name: 'Activity History', href: '/activity', icon: History },
  { name: 'Privacy Settings', href: '/privacy', icon: Shield },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  const handleNavigate = (e: React.MouseEvent, href: string) => {
    e.preventDefault();
    document.cookie = "focusdna-session=active; path=/; max-age=86400; SameSite=Lax";
    router.push(href);
  };

  return (
    <aside className="w-64 border-r border-border/60 bg-card/40 backdrop-blur-md flex flex-col justify-between p-4 min-h-[calc(100vh-4rem)] shrink-0">
      <nav className="space-y-1.5">
        <div className="px-3 py-2 text-xs font-semibold uppercase text-gray-500 tracking-wider">
          Platform Navigation
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href === '/insights' && pathname === '/recommendations') || (item.href === '/activity' && pathname === '/history') || (item.href === '/privacy' && pathname === '/settings');
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={(e) => handleNavigate(e, item.href)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all cursor-pointer ${
                isActive
                  ? 'bg-primary/15 text-primary border border-primary/30 font-semibold shadow-sm'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
              }`}
            >
              <Icon className={`h-4 w-4 ${isActive ? 'text-primary' : 'text-gray-400'}`} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-3.5 rounded-2xl glass-panel border border-border/60">
        <div className="flex items-center gap-2 text-xs font-semibold text-gray-300 mb-1">
          <Compass className="h-4 w-4 text-cyan-400" />
          <span>Real Data Architecture</span>
        </div>
        <p className="text-[11px] text-gray-400 leading-snug">
          Zero fake statistics. Uses real database records & clean empty states.
        </p>
      </div>
    </aside>
  );
}
