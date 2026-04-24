import Link from "next/link";
import { ArrowUpRight, ExternalLink } from "lucide-react";
import { SidebarNav } from "@/components/sidebar-nav";

const externalLinks = [
  { label: "API docs", href: "http://localhost:8000/docs" },
  { label: "MLflow", href: "http://localhost:5500" },
  { label: "Grafana", href: "http://localhost:3100" },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="theme-dark h-screen flex bg-background text-foreground relative overflow-hidden">
      {/* Ambient background glow */}
      <div className="pointer-events-none fixed inset-0 -z-0">
        <div className="absolute top-0 left-1/3 w-[600px] h-[600px] rounded-full bg-brand-gold/10 blur-[140px]" />
        <div className="absolute bottom-0 right-0 w-[500px] h-[500px] rounded-full bg-brand-deep/40 blur-[120px]" />
      </div>

      <aside className="relative z-10 w-64 shrink-0 border-r border-brand-gold/10 bg-[#071a1b]/90 backdrop-blur-xl flex flex-col">
        <div className="p-6 pb-4">
          <Link href="/" className="group flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-brand-gold to-brand-deep border border-brand-gold/40 flex items-center justify-center shadow-gold">
              <span className="font-display text-brand-deepest font-bold text-lg leading-none">
                S
              </span>
            </div>
            <div>
              <div className="font-display text-base tracking-tight text-brand-cream leading-tight">
                Smart Logistics
              </div>
              <div className="text-[10px] tracking-[0.2em] uppercase text-brand-gold/80">
                Decision Copilot
              </div>
            </div>
          </Link>
        </div>

        <div className="h-px bg-gradient-to-r from-transparent via-brand-gold/20 to-transparent mx-4" />

        <SidebarNav />

        <div className="mt-auto p-4 space-y-3">
          <div className="rounded-xl border border-brand-gold/15 bg-brand-deepest/50 p-3 space-y-1.5">
            <div className="text-[10px] uppercase tracking-[0.2em] text-brand-gold/70 mb-1">
              Services
            </div>
            {externalLinks.map((l) => (
              <a
                key={l.href}
                href={l.href}
                target="_blank"
                rel="noreferrer"
                className="flex items-center justify-between text-xs text-muted-foreground hover:text-brand-gold transition-colors"
              >
                <span>{l.label}</span>
                <ExternalLink className="h-3 w-3" />
              </a>
            ))}
          </div>
          <Link
            href="/"
            className="flex items-center justify-between gap-2 rounded-lg px-3 py-2 text-xs text-muted-foreground hover:text-brand-gold hover:bg-brand-gold/5 transition-colors"
          >
            <span>Back to landing</span>
            <ArrowUpRight className="h-3 w-3" />
          </Link>
          <div className="text-[10px] text-muted-foreground/60 px-3">
            Built by <span className="text-brand-gold">Deciwa</span>
          </div>
        </div>
      </aside>

      <main className="relative z-10 flex-1 overflow-auto">
        <div className="max-w-6xl mx-auto p-10 pt-14">{children}</div>
      </main>
    </div>
  );
}
