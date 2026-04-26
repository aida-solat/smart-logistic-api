"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  GitBranch,
  GitCompare,
  MessageSquare,
  PackageSearch,
  Route,
  Sigma,
  Sparkles,
  UserCog,
  Workflow,
  type LucideIcon,
} from "lucide-react";

type Item = {
  href: string;
  label: string;
  icon: LucideIcon;
  group: string;
};

const items: Item[] = [
  { href: "/dashboard", label: "Dashboard", icon: Activity, group: "Overview" },
  { href: "/causal", label: "Causal", icon: GitBranch, group: "Engines" },
  {
    href: "/optimize",
    label: "Optimize",
    icon: PackageSearch,
    group: "Engines",
  },
  { href: "/routing", label: "Routing", icon: Route, group: "Engines" },
  { href: "/simulate", label: "Simulate", icon: Workflow, group: "Engines" },
  {
    href: "/validate",
    label: "Validate A/B",
    icon: GitCompare,
    group: "Quality",
  },
  { href: "/informed", label: "Informed", icon: Sparkles, group: "Quality" },
  {
    href: "/calibration",
    label: "Calibration β",
    icon: Sigma,
    group: "Quality",
  },
  {
    href: "/narrate",
    label: "Narrator",
    icon: MessageSquare,
    group: "Copilot",
  },
  { href: "/feedback", label: "Feedback", icon: UserCog, group: "Copilot" },
];

export function SidebarNav() {
  const pathname = usePathname();

  // group items preserving declaration order
  const groups: { name: string; items: Item[] }[] = [];
  for (const it of items) {
    let g = groups.find((g) => g.name === it.group);
    if (!g) {
      g = { name: it.group, items: [] };
      groups.push(g);
    }
    g.items.push(it);
  }

  return (
    <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-5">
      {groups.map((g) => (
        <div key={g.name}>
          <div className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground/60 px-3 mb-1.5">
            {g.name}
          </div>
          <div className="flex flex-col gap-0.5">
            {g.items.map(({ href, label, icon: Icon }) => {
              const active = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  className={
                    "group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all " +
                    (active
                      ? "bg-brand-indigo/10 text-brand-cream"
                      : "text-muted-foreground hover:text-brand-cream hover:bg-white/5")
                  }
                >
                  {active && (
                    <span className="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-[3px] rounded-r bg-brand-indigo shadow-indigo" />
                  )}
                  <Icon
                    className={
                      "h-4 w-4 transition-colors " +
                      (active
                        ? "text-brand-indigo"
                        : "group-hover:text-brand-indigo")
                    }
                  />
                  <span>{label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      ))}
    </nav>
  );
}
