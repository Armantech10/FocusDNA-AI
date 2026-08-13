import './globals.css';
import type { Metadata } from 'next';
import { Navbar } from '@/components/Navbar';

export const metadata: Metadata = {
  title: 'FocusDNA AI — Predictive Attention Intelligence Shell',
  description: 'Privacy-first digital wellness foundation platform.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background text-foreground antialiased flex flex-col">
        <Navbar />
        <main className="flex-1">
          {children}
        </main>
      </body>
    </html>
  );
}
