"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Database,
  Flame,
  GitBranch,
  LogOut,
  PackageSearch,
  Route,
  Shield,
  Sparkles,
  Workflow,
  type LucideIcon,
} from "lucide-react";
import { api, auth } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/page-header";

export default function Dashboard() {
  const [health, setHealth] = useState<"loading" | "ok" | "fail">("loading");
  const [detail, setDetail] = useState<string>("");
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => setToken(auth.getToken()), []);

  async function doLogin() {
    try {
      const t = await auth.login("admin");
      setToken(t);
    } catch (e) {
      alert(String(e));
    }
  }
  function doLogout() {
    auth.setToken(null);
    setToken(null);
  }

  useEffect(() => {
    api
      .health()
      .then((r) => {
        setHealth(r.status === "healthy" ? "ok" : "fail");
        setDetail(JSON.stringify(r));
      })
      .catch((e) => {
        setHealth("fail");
        setDetail(String(e));
      });
  }, []);

  const quickActions = [
    {
      href: "/informed",
      label: "Run informed pipeline",
      sub: "Causal → CVaR end-to-end",
      icon: Sparkles,
      featured: true,
    },
    {
      href: "/causal",
      label: "Estimate causal effect",
      sub: "DoWhy counterfactual",
      icon: GitBranch,
    },
    {
      href: "/optimize",
      label: "Solve CVaR inventory",
      sub: "Rockafellar–Uryasev",
      icon: PackageSearch,
    },
    {
      href: "/routing",
      label: "Risk-aware VRP",
      sub: "OR-Tools + Monte-Carlo",
      icon: Route,
    },
    {
      href: "/simulate",
      label: "Run digital twin",
      sub: "SimPy Monte-Carlo KPIs",
      icon: Workflow,
    },
    {
      href: "/validate",
      label: "A/B validate decision",
      sub: "Pareto uplift report",
      icon: BarChart3,
    },
  ];

  return (
    <div className="space-y-10">
      <PageHeader
        kicker="Mission control"
        title="Welcome back, operator."
        icon={Activity}
        description="Every engine in your causal decision pipeline, one click away. All stages are MLflow-logged."
        actions={
          token ? (
            <Button variant="outline" size="sm" onClick={doLogout}>
              <LogOut className="h-3.5 w-3.5" />
              Logout
            </Button>
          ) : (
            <Button onClick={doLogin}>
              <Shield className="h-4 w-4" />
              Login as admin
            </Button>
          )
        }
      />

      {/* Hero stat row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <HealthCard status={health} detail={detail} />
        <StatCard
          icon={Database}
          label="Dataset"
          value="Olist 95k"
          sub="Brazilian e-commerce · 2016-18"
        />
        <StatCard
          icon={Flame}
          label="Engines shipped"
          value="7 / 9"
          sub="Phases 0 through 6"
        />
        <StatCard
          icon={Shield}
          label="Auth"
          value={token ? "Active" : "Guest"}
          sub={token ? "JWT in localStorage" : "Some endpoints locked"}
          accent={!token}
        />
      </div>

      {/* Quick actions grid */}
      <section>
        <SectionHeader
          kicker="Quick actions"
          title="Jump into an engine"
          sub="Each link runs a live endpoint against the backend."
        />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {quickActions.map((a) => (
            <Link
              key={a.href}
              href={a.href}
              className={
                "card-3d group rounded-2xl p-6 flex items-start gap-4 hover:-translate-y-1 transition-transform duration-300 " +
                (a.featured ? "!border-brand-gold/50" : "")
              }
            >
              <div className="orb-chip !w-12 !h-12 !rounded-xl shrink-0 !transform-none">
                <a.icon
                  className="h-5 w-5 text-brand-deepest relative z-10"
                  strokeWidth={2.2}
                />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h4 className="font-display text-lg text-brand-cream leading-tight">
                    {a.label}
                  </h4>
                  {a.featured && (
                    <span className="text-[9px] uppercase tracking-[0.2em] px-1.5 py-0.5 rounded bg-brand-gold/15 text-brand-gold border border-brand-gold/30">
                      Star
                    </span>
                  )}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {a.sub}
                </div>
              </div>
              <ArrowRight className="h-4 w-4 text-brand-gold/60 group-hover:text-brand-gold group-hover:translate-x-1 transition-all shrink-0 mt-2" />
            </Link>
          ))}
        </div>
      </section>

      {/* Pipeline timeline */}
      <section>
        <SectionHeader
          kicker="Pipeline"
          title="What's live in this build"
          sub="Timeline of shipped phases."
        />
        <Card>
          <CardContent className="pt-6 space-y-0">
            <Stage
              phase="Phase 0"
              label="Scaffold · auth · Docker stack"
              first
            />
            <Stage
              phase="Phase 1"
              label="Causal engine on Olist (DoWhy + MLflow)"
            />
            <Stage
              phase="Phase 2"
              label="CVaR stochastic optimizer (Rockafellar–Uryasev LP)"
            />
            <Stage
              phase="Phase 3"
              label="SimPy digital twin with Monte-Carlo KPIs"
            />
            <Stage
              phase="Phase 4"
              label="Risk-aware VRP (OR-Tools + makespan CVaR)"
            />
            <Stage
              phase="Phase 5"
              label="Causal-informed CVaR end-to-end pipeline"
            />
            <Stage
              phase="Phase 6"
              label="Next.js cockpit — you are here"
              active
              last
            />
          </CardContent>
        </Card>
      </section>

      {/* Token debug drawer */}
      {token && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="!text-base">Active session token</CardTitle>
              <span className="text-[10px] uppercase tracking-[0.2em] text-brand-gold">
                JWT · localStorage
              </span>
            </div>
          </CardHeader>
          <CardContent>
            <code className="block text-[11px] font-mono text-muted-foreground bg-brand-deepest/50 border border-brand-gold/10 rounded-lg px-3 py-2 truncate">
              {token}
            </code>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

/* ---------------------------- Sub-components ---------------------------- */

function HealthCard({
  status,
  detail,
}: {
  status: "loading" | "ok" | "fail";
  detail: string;
}) {
  const dot =
    status === "ok"
      ? "bg-emerald-400 shadow-[0_0_14px_2px_rgba(52,211,153,0.6)]"
      : status === "fail"
        ? "bg-red-400 shadow-[0_0_14px_2px_rgba(248,113,113,0.6)]"
        : "bg-yellow-400 animate-shimmer";
  const label =
    status === "ok"
      ? "Healthy"
      : status === "fail"
        ? "Unreachable"
        : "Checking…";
  return (
    <Card className="p-5 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="text-[10px] uppercase tracking-[0.2em] text-brand-gold/80">
          API status
        </div>
        <div className={`h-2.5 w-2.5 rounded-full ${dot}`} />
      </div>
      <div className="font-display text-3xl text-brand-cream">{label}</div>
      <div className="text-[10px] text-muted-foreground/70 truncate">
        {status === "ok" ? "GET /health" : status === "fail" ? detail : "…"}
      </div>
    </Card>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  sub,
  accent,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
  sub: string;
  accent?: boolean;
}) {
  return (
    <Card className="p-5 flex flex-col gap-3 hover:-translate-y-1 transition-transform duration-300">
      <div className="flex items-center justify-between">
        <div className="text-[10px] uppercase tracking-[0.2em] text-brand-gold/80">
          {label}
        </div>
        <Icon
          className={
            "h-4 w-4 " +
            (accent ? "text-brand-gold" : "text-muted-foreground/70")
          }
          strokeWidth={2}
        />
      </div>
      <div className="font-display text-3xl text-brand-cream">{value}</div>
      <div className="text-[10px] text-muted-foreground/70">{sub}</div>
    </Card>
  );
}

function SectionHeader({
  kicker,
  title,
  sub,
}: {
  kicker: string;
  title: string;
  sub: string;
}) {
  return (
    <div className="mb-5">
      <div className="text-[11px] uppercase tracking-[0.25em] text-brand-gold">
        {kicker}
      </div>
      <h2 className="mt-1 font-display text-2xl text-brand-cream">{title}</h2>
      <p className="text-sm text-muted-foreground">{sub}</p>
    </div>
  );
}

function Stage({
  phase,
  label,
  active,
  first,
  last,
}: {
  phase: string;
  label: string;
  active?: boolean;
  first?: boolean;
  last?: boolean;
}) {
  return (
    <div className="relative flex items-start gap-4 py-3">
      {/* vertical line */}
      {!last && (
        <span className="absolute left-[14px] top-8 bottom-0 w-px bg-brand-gold/15" />
      )}
      <div
        className={
          "relative z-10 h-7 w-7 rounded-full flex items-center justify-center shrink-0 " +
          (active
            ? "bg-brand-gold shadow-gold"
            : "bg-brand-deepest border border-brand-gold/30")
        }
      >
        <CheckCircle2
          className={
            "h-4 w-4 " + (active ? "text-brand-deepest" : "text-brand-gold/80")
          }
          strokeWidth={2.4}
        />
      </div>
      <div className="flex-1 pt-1">
        <div className="text-[10px] uppercase tracking-[0.2em] text-brand-gold/80">
          {phase} {active && "· active"}
        </div>
        <div
          className={
            "text-sm " +
            (active ? "text-brand-cream font-medium" : "text-muted-foreground")
          }
        >
          {label}
        </div>
      </div>
    </div>
  );
}
