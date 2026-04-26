import Link from "next/link";
import { ArrowUpRight, ExternalLink } from "lucide-react";
import { SidebarNav } from "@/components/sidebar-nav";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const MLFLOW_URL = process.env.NEXT_PUBLIC_MLFLOW_URL;
const GRAFANA_URL = process.env.NEXT_PUBLIC_GRAFANA_URL;

const externalLinks = [
  { label: "API docs", href: `${API_URL}/docs` },
  ...(MLFLOW_URL ? [{ label: "MLflow", href: MLFLOW_URL }] : []),
  ...(GRAFANA_URL ? [{ label: "Grafana", href: GRAFANA_URL }] : []),
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="h-screen flex bg-background text-foreground relative overflow-hidden">
      <div className="pointer-events-none fixed inset-0 -z-0 bg-[radial-gradient(ellipse_at_top_right,rgba(99,91,255,0.05),transparent_60%)]" />

      <aside className="relative z-10 w-64 shrink-0 border-r border-zinc-200 bg-white/80 backdrop-blur-xl flex flex-col">
        <div className="p-6 pb-4">
          <Link href="/" className="group flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-lg bg-brand-gold border border-brand-gold/40 flex items-center justify-center shadow-gold">
              <span className="font-display text-white font-bold text-lg leading-none">
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
