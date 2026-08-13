'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Target, ArrowRight } from 'lucide-react';

interface EmptyStateProps {
  icon?: React.ElementType;
  title: string;
  description: string;
  actionText?: string;
  actionHref?: string;
  onActionClick?: () => void;
}

export function EmptyState({
  icon: Icon = Target,
  title,
  description,
  actionText = "Start Your First Focus Session",
  actionHref = "/focus",
  onActionClick
}: EmptyStateProps) {
  const router = useRouter();

  const handleLinkClick = (e: React.MouseEvent) => {
    if (onActionClick) {
      onActionClick();
      return;
    }
    if (actionHref) {
      e.preventDefault();
      document.cookie = "focusdna-session=active; path=/; max-age=86400; SameSite=Lax";
      router.push(actionHref);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center p-8 sm:p-12 text-center rounded-3xl glass-panel border border-border/80 space-y-4 my-2">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 border border-primary/30 text-primary shadow-lg shadow-primary/10">
        <Icon className="h-7 w-7" />
      </div>

      <div className="space-y-1.5 max-w-md">
        <h3 className="text-lg font-bold text-white tracking-tight">{title}</h3>
        <p className="text-xs sm:text-sm text-gray-400 leading-relaxed">{description}</p>
      </div>

      {actionText && actionHref && (
        <div className="pt-2">
          <button
            onClick={handleLinkClick}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-primary text-white text-xs font-bold shadow-lg shadow-primary/30 hover:bg-primary-hover transition-all cursor-pointer"
          >
            <span>{actionText}</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}
