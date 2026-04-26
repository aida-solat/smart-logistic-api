import Link from "next/link";
import HeroVisual from "@/components/hero-visual";
import {
  ArrowRight,
  BrainCircuit,
  GitBranch,
  Heart,
  PackageSearch,
  Route,
  Shield,
  ShieldCheck,
  Target,
  Workflow,
  Coffee,
  Scale,
  FileText,
  TrendingUp,
  Lock,
} from "lucide-react";

function Github({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden="true"
      className={className}
    >
      <path d="M12 .5C5.73.5.5 5.73.5 12a11.5 11.5 0 0 0 7.86 10.94c.57.1.78-.25.78-.55v-1.92c-3.2.7-3.88-1.54-3.88-1.54-.52-1.33-1.28-1.68-1.28-1.68-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.2 1.77 1.2 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.73-1.55-2.55-.29-5.23-1.28-5.23-5.7 0-1.26.45-2.3 1.2-3.1-.12-.3-.52-1.48.11-3.1 0 0 .98-.31 3.2 1.18a11 11 0 0 1 5.82 0c2.22-1.5 3.2-1.18 3.2-1.18.63 1.62.23 2.8.11 3.1.75.8 1.2 1.84 1.2 3.1 0 4.43-2.69 5.4-5.25 5.69.41.36.77 1.06.77 2.14v3.17c0 .3.2.66.79.55A11.5 11.5 0 0 0 23.5 12C23.5 5.73 18.27.5 12 .5Z" />
    </svg>
  );
}

const GITHUB_USER = "aida-solat";
const GITHUB_REPO = "smart-logistic-api";
const KO_FI = "aidasolat";

export default function Landing() {
  return (
    <div className="bg-background text-foreground min-h-screen">
      <Nav />
      <Hero />
      <Problem />
      <Novelty />
      <HowItWorks />
      <TechStack />
      <Audience />
      <Roadmap />
      <Sponsor />
      <Contribute />
      <Footer />
    </div>
  );
}

function Nav() {
  return (
    <header className="sticky top-0 z-40 backdrop-blur-md bg-brand-deepest/70 border-b border-brand-indigo/10">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <LogoMark />
          <span className="font-display text-lg tracking-tight text-brand-cream">
            Smart Logistics
          </span>
        </Link>
        <nav className="hidden md:flex items-center gap-7 text-sm text-muted-foreground">
          <a href="#problem" className="hover:text-brand-indigo transition">
            Problem
          </a>
          <a href="#novelty" className="hover:text-brand-indigo transition">
            Novelty
          </a>
          <a href="#stack" className="hover:text-brand-indigo transition">
            Stack
          </a>
          <a href="#roadmap" className="hover:text-brand-indigo transition">
            Roadmap
          </a>
          <a href="#sponsor" className="hover:text-brand-indigo transition">
            Sponsor
          </a>
        </nav>
        <div className="flex items-center gap-3">
          <a
            href={`https://github.com/${GITHUB_USER}/${GITHUB_REPO}`}
            target="_blank"
            rel="noreferrer"
            className="hidden sm:inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-brand-indigo transition"
            aria-label="GitHub repository"
          >
            <Github className="h-4 w-4" />
            Star
          </a>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 rounded-md bg-brand-indigo text-brand-deepest px-4 py-2 text-sm font-medium hover:shadow-indigo transition-shadow"
          >
            Launch app
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </header>
  );
}

function LogoMark() {
  return (
    <div className="relative h-8 w-8 rounded-lg bg-brand-indigo border border-brand-indigo/40 flex items-center justify-center">
      <span className="font-display text-white font-bold text-lg leading-none">
        S
      </span>
    </div>
  );
}

function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-brand-indigo/10">
      <div className="hero-bg" />
      <div className="absolute inset-0 hero-grid pointer-events-none" />

      <div className="max-w-7xl mx-auto px-6 pt-20 pb-24 relative grid lg:grid-cols-12 gap-12 items-center">
        <div className="lg:col-span-7">
          <div className="inline-flex items-center gap-2 rounded-full border border-brand-indigo/30 bg-brand-indigo/5 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-brand-indigo mb-8">
            <span className="h-1.5 w-1.5 rounded-full bg-brand-indigo" />
            Causal decision platform
          </div>
          <div className="max-w-3xl">
            <h1 className="font-display text-4xl md:text-6xl tracking-tight leading-[1.1] text-brand-cream">
              Prescriptive logistics, <br />
              <span className="shine">backed by causal evidence.</span>
            </h1>
            <p className="mt-6 max-w-2xl text-base md:text-lg text-muted-foreground leading-relaxed">
              An enterprise-grade decision engine that combines causal
              inference, risk-aware stochastic optimization, and a digital twin
              to recommend the next operational action — and certify the uplift
              offline before deployment.
            </p>
            <div className="mt-10 flex flex-wrap gap-3">
              <Link
                href="/informed"
                className="inline-flex items-center gap-2 rounded-md bg-brand-indigo text-brand-deepest px-5 py-2.5 text-sm font-semibold hover:brightness-110 transition"
              >
                Try the live pipeline
                <ArrowRight className="h-4 w-4" />
              </Link>
              <a
                href={`https://github.com/${GITHUB_USER}/${GITHUB_REPO}`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 rounded-md border border-brand-indigo/40 px-5 py-2.5 text-sm font-medium text-brand-indigo hover:bg-brand-indigo/10 transition"
              >
                <Github className="h-4 w-4" />
                Source on GitHub
              </a>
            </div>
          </div>
        </div>

        <div className="lg:col-span-5">
          <HeroVisual />
        </div>

        <div className="lg:col-span-12 mt-8 grid grid-cols-2 md:grid-cols-4 gap-x-10 gap-y-8 max-w-4xl relative">
          <Metric
            value="+89%"
            label="service level uplift"
            sub="A/B digital twin"
          />
          <Metric value="−81%" label="total cost" sub="same scenario" />
          <Metric value="95k" label="Olist orders" sub="real training data" />
          <Metric
            value="CVaR₀.₉₅"
            label="tail-risk optimal"
            sub="Rockafellar–Uryasev"
          />
        </div>
      </div>
    </section>
  );
}

function Metric({
  value,
  label,
  sub,
}: {
  value: string;
  label: string;
  sub: string;
}) {
  return (
    <div className="border-l-2 border-brand-indigo/60 pl-4">
      <div className="font-display text-3xl text-brand-cream tabular-nums">
        {value}
      </div>
      <div className="text-sm text-muted-foreground mt-1">{label}</div>
      <div className="text-[11px] text-muted-foreground/60 uppercase tracking-wider mt-0.5">
        {sub}
      </div>
    </div>
  );
}

function Problem() {
  return (
    <Section
      id="problem"
      kicker="The problem"
      title="Logistics AI is stuck predicting the past."
    >
      <div className="grid md:grid-cols-2 gap-10">
        <div className="space-y-4 text-muted-foreground leading-relaxed">
          <p>
            Every operations team drowns in dashboards that scream{" "}
            <em>&ldquo;this shipment will be late&rdquo;</em> — but none of them
            tell the manager <em>what to actually do</em>, or what happens if
            they don&apos;t.
          </p>
          <p>
            The right question is{" "}
            <span className="text-brand-indigo">causal</span>: &ldquo;If I move
            200 units from warehouse A to B today, what is the worst-case cost I
            should expect next month?&rdquo; Answering that requires
            do-calculus, tail-risk optimization, and a simulator — not another
            gradient-boosted ETA.
          </p>
          <p>
            Smart Logistics is the first open platform to wire all three
            together into a single closed loop with a fully auditable trail.
          </p>
        </div>
        <div className="space-y-3">
          <BadRow
            text='"How late will this shipment be?"'
            label="predictive"
            bad
          />
          <BadRow
            text='"What is the expected delivery time?"'
            label="forecast"
            bad
          />
          <BadRow
            text='"Cluster customers by behavior."'
            label="descriptive"
            bad
          />
          <BadRow
            text='"What should I do now, and what if I don’t?"'
            label="prescriptive"
          />
          <BadRow
            text='"Is the proposed decision Pareto-improving?"'
            label="causal + simulation"
          />
          <BadRow
            text='"How will tail risk shift under policy X?"'
            label="CVaR-aware"
          />
        </div>
      </div>
    </Section>
  );
}

function BadRow({
  text,
  label,
  bad,
}: {
  text: string;
  label: string;
  bad?: boolean;
}) {
  return (
    <div
      className={`flex items-center justify-between gap-4 rounded-lg border px-4 py-3 ${
        bad
          ? "border-destructive/20 bg-destructive/5 opacity-60"
          : "border-brand-indigo/30 bg-brand-indigo/5"
      }`}
    >
      <span className={bad ? "line-through" : "text-brand-cream"}>{text}</span>
      <span
        className={`text-[11px] uppercase tracking-widest ${
          bad ? "text-destructive/70" : "text-brand-indigo"
        }`}
      >
        {label}
      </span>
    </div>
  );
}

function Novelty() {
  const claims = [
    {
      n: "01",
      icon: BrainCircuit,
      title: "Causal-informed CVaR",
      text: "A DoWhy average-treatment-effect estimate modulates the stockout penalty of a Rockafellar–Uryasev CVaR linear program. First open implementation.",
    },
    {
      n: "02",
      icon: TrendingUp,
      title: "Closed-loop β calibration",
      text: "Post-deployment realized costs are logged and refit via OLS, so penalty sensitivity β adapts to your operation — no manual tuning.",
    },
    {
      n: "03",
      icon: Workflow,
      title: "Digital-twin A/B validation",
      text: "Every prescriptive decision is certified Pareto-improving in a SimPy twin before it ever reaches production.",
    },
    {
      n: "04",
      icon: Route,
      title: "Risk-aware VRP scoring",
      text: "OR-Tools deterministic CVRP is re-scored with Monte-Carlo CVaR of makespan under travel-time noise for route robustness.",
    },
  ];
  return (
    <Section
      id="novelty"
      kicker="The novelty"
      title="Four novel claims, all implemented & tested."
    >
      <div className="grid md:grid-cols-2 gap-x-12 gap-y-2">
        {claims.map((c) => (
          <div
            key={c.n}
            className="group relative py-8 border-t border-brand-indigo/15 flex gap-6"
          >
            <div className="font-display text-5xl tabular-nums text-brand-indigo/30 group-hover:text-brand-indigo transition-colors leading-none shrink-0 w-14">
              {c.n}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-3">
                <c.icon className="h-4 w-4 text-brand-indigo" strokeWidth={2} />
                <span className="text-[10px] uppercase tracking-[0.22em] text-muted-foreground">
                  Claim {c.n}
                </span>
              </div>
              <h3 className="font-display text-xl text-brand-cream leading-snug">
                {c.title}
              </h3>
              <p className="mt-2.5 text-sm text-muted-foreground leading-relaxed">
                {c.text}
              </p>
            </div>
          </div>
        ))}
      </div>
    </Section>
  );
}

function HowItWorks() {
  const steps = [
    { icon: GitBranch, label: "Causal", sub: "DoWhy ATE" },
    { icon: Target, label: "Penalty", sub: "β · Δ·ATE" },
    { icon: PackageSearch, label: "CVaR LP", sub: "Rockafellar–Uryasev" },
    { icon: Route, label: "Risk VRP", sub: "OR-Tools + MC" },
    { icon: Workflow, label: "Digital Twin", sub: "SimPy A/B" },
    { icon: TrendingUp, label: "β refit", sub: "OLS on log" },
  ];
  return (
    <Section
      kicker="How it works"
      title="One closed loop. Every stage MLflow-logged."
    >
      <div className="relative">
        {/* Connector line behind icons */}
        <div className="hidden md:block absolute left-0 right-0 top-7 h-px bg-gradient-to-r from-transparent via-brand-indigo/40 to-transparent pointer-events-none" />
        <div className="relative grid grid-cols-2 md:grid-cols-7 gap-y-8 gap-x-2">
          {steps.map((s) => (
            <div
              key={s.label}
              className="flex flex-col items-center text-center group"
            >
              <div className="h-14 w-14 rounded-2xl bg-white border border-zinc-200 shadow-[0_1px_3px_0_rgba(15,23,42,0.06),0_4px_12px_-4px_rgba(99,91,255,0.18)] flex items-center justify-center group-hover:-translate-y-1 transition-transform">
                <s.icon
                  className="h-5 w-5 text-brand-indigo"
                  strokeWidth={2.2}
                />
              </div>
              <div className="mt-3 text-sm text-brand-cream font-semibold">
                {s.label}
              </div>
              <div className="text-[10px] uppercase tracking-wider text-muted-foreground mt-0.5">
                {s.sub}
              </div>
            </div>
          ))}
        </div>
        <p className="mt-12 text-sm text-muted-foreground max-w-2xl leading-relaxed">
          Every box is a tested FastAPI endpoint. Every arrow is an integration
          test. Every artifact — model, scenario set, decision, KPI uplift — is
          persisted in MLflow as experimental evidence. The live demo runs on
          Vercel + Render; the full monitoring stack (MLflow, Prometheus,
          Grafana) ships with the repo via{" "}
          <code className="text-brand-indigo">docker compose up</code>.
        </p>
      </div>
    </Section>
  );
}

function TechStack() {
  const groups = [
    {
      name: "Causal ML",
      items: ["DoWhy", "EconML", "scikit-learn", "statsmodels"],
    },
    {
      name: "Optimization",
      items: [
        "CVXPY",
        "OR-Tools",
        "Rockafellar–Uryasev LP",
        "Monte-Carlo CVaR",
      ],
    },
    {
      name: "Simulation",
      items: ["SimPy", "A/B offline backtest", "Monte-Carlo KPIs"],
    },
    {
      name: "Backend",
      items: [
        "FastAPI",
        "SQLAlchemy",
        "Alembic",
        "PostgreSQL",
        "Redis",
        "Pydantic v2",
      ],
    },
    {
      name: "Frontend",
      items: [
        "Next.js 16",
        "React 19",
        "TypeScript 6",
        "Tailwind CSS 4",
        "Radix UI",
        "Recharts 3",
        "react-three-fiber",
      ],
    },
    {
      name: "AI / Copilot",
      items: [
        "OpenAI chat API",
        "LLM narrator",
        "operator Q&A",
        "feedback loop",
      ],
    },
    {
      name: "Ops",
      items: [
        "Docker Compose",
        "MLflow (local)",
        "Prometheus (local)",
        "Grafana (local)",
        "GitHub Actions",
      ],
    },
    {
      name: "Deploy",
      items: [
        "Vercel — frontend",
        "Render — API + DB + Redis",
        "cron-job.org — keep-alive",
      ],
    },
  ];
  return (
    <Section
      id="stack"
      kicker="Tech stack"
      title="Boring, battle-tested, open source."
    >
      <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-5">
        {groups.map((g) => (
          <div
            key={g.name}
            className="card-3d rounded-2xl p-6 hover:-translate-y-1 transition-transform duration-300"
          >
            <div className="text-[11px] uppercase tracking-[0.2em] text-brand-indigo">
              {g.name}
            </div>
            <ul className="mt-3 space-y-1.5">
              {g.items.map((i) => (
                <li
                  key={i}
                  className="text-sm text-brand-cream/90 flex items-center gap-2"
                >
                  <span className="h-1 w-1 rounded-full bg-brand-indigo" /> {i}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </Section>
  );
}

function Audience() {
  const who = [
    {
      title: "Supply-chain & ops teams",
      text: "Replace your delivery-time dashboard with a decision copilot that recommends reallocations and proves the uplift.",
    },
    {
      title: "3PL & last-mile operators",
      text: "Get risk-aware vehicle routing that is robust to traffic shocks, not just optimal on paper.",
    },
    {
      title: "E-commerce platforms",
      text: "Causal inventory reallocation across warehouses to defend service-level under demand uncertainty.",
    },
    {
      title: "OR / causal-ML researchers",
      text: "A real, reproducible end-to-end stack to benchmark your algorithm on a public dataset (Olist).",
    },
    {
      title: "Logistics consultancies",
      text: "White-label the UI, swap the dataset, deliver prescriptive recommendations with an audit trail.",
    },
    {
      title: "Research auditors",
      text: "Every component is MLflow-logged with timestamps — ready-made experimental evidence.",
    },
  ];
  return (
    <Section
      kicker="Who is it for"
      title="Anyone who needs to decide, not just predict."
    >
      <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-5">
        {who.map((w) => (
          <div
            key={w.title}
            className="card-3d rounded-2xl p-6 hover:-translate-y-1 transition-transform duration-300"
          >
            <h4 className="font-display text-xl text-brand-cream">{w.title}</h4>
            <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
              {w.text}
            </p>
          </div>
        ))}
      </div>
    </Section>
  );
}

function Roadmap() {
  const phases: {
    name: string;
    status: "done" | "next" | "future";
    items: string[];
  }[] = [
    {
      name: "Shipped",
      status: "done",
      items: [
        "Causal engine on Olist (DoWhy + MLflow)",
        "CVaR inventory LP (Rockafellar–Uryasev)",
        "Risk-aware VRP (OR-Tools + MC)",
        "SimPy digital twin + A/B validation",
        "Adaptive β calibration loop",
        "Next.js 16 + Radix UI cockpit",
        "LLM narrator + feedback loop",
      ],
    },
    {
      name: "Next",
      status: "next",
      items: [
        "Real-time streaming ingestion (Kafka)",
        "Multi-echelon inventory (plants → hubs → stores)",
      ],
    },
    {
      name: "Vision",
      status: "future",
      items: [
        "Federated causal learning across logistics networks",
        "Causal LLM agents that execute decisions autonomously",
        "Managed SaaS with private data connectors",
      ],
    },
  ];
  return (
    <Section
      id="roadmap"
      kicker="Where it's going"
      title="The path from open-source repo to global platform."
    >
      <div className="grid md:grid-cols-3 gap-5">
        {phases.map((p) => (
          <div
            key={p.name}
            className={`card-3d rounded-2xl p-7 hover:-translate-y-1 transition-transform duration-300 ${
              p.status === "done" ? "!border-brand-indigo/50" : ""
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="text-[11px] uppercase tracking-[0.2em] text-brand-indigo">
                {p.name}
              </div>
              <div className="text-[11px] text-muted-foreground capitalize">
                {p.status}
              </div>
            </div>
            <ul className="mt-4 space-y-2">
              {p.items.map((it) => (
                <li key={it} className="flex gap-2 text-sm text-brand-cream/90">
                  <span className="text-brand-indigo mt-1">◆</span>
                  <span>{it}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </Section>
  );
}

function Sponsor() {
  return (
    <section id="sponsor" className="border-b border-brand-indigo/10">
      <div className="max-w-7xl mx-auto px-6 py-24">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-brand-indigo to-[#4f46e5] text-white">
          {/* Decorative grid + glow */}
          <div className="absolute inset-0 opacity-20 [background-image:linear-gradient(rgba(255,255,255,0.15)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.15)_1px,transparent_1px)] [background-size:32px_32px] pointer-events-none" />
          <div className="absolute -top-32 -right-32 h-80 w-80 rounded-full bg-white/10 blur-3xl pointer-events-none" />

          <div className="relative grid md:grid-cols-12 gap-10 p-10 md:p-14 items-center">
            <div className="md:col-span-7">
              <div className="inline-flex items-center gap-2 rounded-full bg-white/15 backdrop-blur px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-white">
                <Heart className="h-3 w-3" />
                Sponsor the project
              </div>
              <h2 className="mt-5 font-display text-3xl md:text-4xl tracking-tight leading-tight">
                Open-source, forever.
                <br />
                Powered by people like you.
              </h2>
              <p className="mt-4 text-white/80 max-w-lg leading-relaxed">
                Every dollar funds causal benchmarks on new datasets and keeps
                the Docker stack running for the community.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <a
                  href={`https://github.com/sponsors/${GITHUB_USER}`}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 rounded-md bg-white text-brand-indigo px-5 py-2.5 text-sm font-semibold hover:bg-white/90 transition"
                >
                  <Github className="h-4 w-4" /> Sponsor on GitHub
                </a>
                <a
                  href={`https://ko-fi.com/${KO_FI}`}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 rounded-md border border-white/40 px-5 py-2.5 text-sm font-medium text-white hover:bg-white/10 transition"
                >
                  <Coffee className="h-4 w-4" /> Ko-fi
                </a>
              </div>
            </div>

            <div className="md:col-span-5">
              <div className="grid grid-cols-2 gap-3">
                <SponsorTier amount="$5" label="Coffee" sub="per month" />
                <SponsorTier amount="$25" label="Backer" sub="per month" />
                <SponsorTier amount="$100" label="Sustainer" sub="per month" />
                <SponsorTier amount="✨" label="Custom" sub="reach out" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function SponsorTier({
  amount,
  label,
  sub,
}: {
  amount: string;
  label: string;
  sub: string;
}) {
  return (
    <div className="rounded-xl bg-white/10 backdrop-blur border border-white/15 p-4 hover:bg-white/15 transition">
      <div className="font-display text-2xl tabular-nums">{amount}</div>
      <div className="text-sm font-medium mt-1">{label}</div>
      <div className="text-[10px] uppercase tracking-wider text-white/60 mt-0.5">
        {sub}
      </div>
    </div>
  );
}

function Contribute() {
  const cards = [
    {
      icon: Github,
      title: "Contribute on GitHub",
      text: "Issues tagged good-first-issue, causal, optimizer, simulator. PRs welcome.",
      href: `https://github.com/${GITHUB_USER}/${GITHUB_REPO}`,
      cta: "Open repo",
    },
    {
      icon: BrainCircuit,
      title: "Benchmark your algorithm",
      text: "Plug your causal estimator or solver into our pipeline and publish uplift numbers.",
      href: `https://github.com/${GITHUB_USER}/${GITHUB_REPO}/blob/main/back/README.md`,
      cta: "Read docs",
    },
    {
      icon: ShieldCheck,
      title: "Report a vulnerability",
      text: "Security disclosures are handled privately — see our policy.",
      href: `https://github.com/${GITHUB_USER}/${GITHUB_REPO}/security/policy`,
      cta: "Security policy",
    },
  ];
  return (
    <Section
      id="contribute"
      kicker="Contribute"
      title="Build the future of prescriptive logistics with us."
    >
      <div className="grid md:grid-cols-3 gap-x-12 gap-y-2">
        {cards.map((c, i) => (
          <a
            key={c.title}
            href={c.href}
            target="_blank"
            rel="noreferrer"
            className="group relative py-8 border-t border-brand-indigo/15 flex gap-5 hover:border-brand-indigo/40 transition-colors"
          >
            <div className="font-display text-4xl tabular-nums text-brand-indigo/30 group-hover:text-brand-indigo transition-colors leading-none shrink-0 w-10">
              {String(i + 1).padStart(2, "0")}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-3">
                <c.icon className="h-4 w-4 text-brand-indigo" strokeWidth={2} />
                <span className="text-[10px] uppercase tracking-[0.22em] text-muted-foreground">
                  Way {i + 1}
                </span>
              </div>
              <h4 className="font-display text-xl text-brand-cream leading-snug">
                {c.title}
              </h4>
              <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                {c.text}
              </p>
              <div className="mt-4 inline-flex items-center gap-1.5 text-xs font-medium text-brand-indigo group-hover:gap-2.5 transition-all">
                {c.cta}
                <ArrowRight className="h-3 w-3" />
              </div>
            </div>
          </a>
        ))}
      </div>
    </Section>
  );
}

function Footer() {
  const legal = [
    {
      icon: Scale,
      label: "MIT License",
      href: `https://github.com/${GITHUB_USER}/${GITHUB_REPO}/blob/main/LICENSE`,
    },
    {
      icon: Lock,
      label: "Security",
      href: `https://github.com/${GITHUB_USER}/${GITHUB_REPO}/blob/main/SECURITY.md`,
    },
    {
      icon: FileText,
      label: "Contributing",
      href: `https://github.com/${GITHUB_USER}/${GITHUB_REPO}/blob/main/CONTRIBUTING.md`,
    },
    {
      icon: Shield,
      label: "Code of Conduct",
      href: `https://github.com/${GITHUB_USER}/${GITHUB_REPO}/blob/main/CODE_OF_CONDUCT.md`,
    },
  ];
  return (
    <footer className="border-t border-brand-indigo/10 bg-brand-deepest">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-8">
          <div>
            <div className="flex items-center gap-2">
              <LogoMark />
              <span className="font-display text-lg tracking-tight text-brand-cream">
                Smart Logistics
              </span>
            </div>
            <p className="mt-3 text-sm text-muted-foreground max-w-md">
              A causal decision copilot for logistics. Designed &amp; built by{" "}
              <a
                href="https://github.com/aida-solat"
                target="_blank"
                rel="noreferrer"
                className="text-brand-indigo hover:underline"
              >
                Deciwa
              </a>
              .
            </p>
          </div>
          <div className="flex flex-wrap gap-x-6 gap-y-2">
            {legal.map((l) => (
              <a
                key={l.label}
                href={l.href}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-brand-indigo transition"
              >
                <l.icon className="h-4 w-4" />
                {l.label}
              </a>
            ))}
          </div>
        </div>
        <div className="mt-10 pt-6 border-t border-brand-indigo/10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-xs text-muted-foreground">
          <div>© {new Date().getFullYear()} Deciwa. </div>
          <div>
            <Link
              href="/dashboard"
              className="text-brand-indigo hover:underline"
            >
              Launch the app →
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}

function Section({
  id,
  kicker,
  title,
  children,
}: {
  id?: string;
  kicker: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className="border-b border-brand-indigo/10">
      <div className="max-w-7xl mx-auto px-6 py-24">
        <div className="text-[11px] uppercase tracking-[0.25em] text-brand-indigo">
          {kicker}
        </div>
        <h2 className="mt-4 font-display text-3xl md:text-5xl tracking-tight text-brand-cream max-w-3xl leading-tight">
          {title}
        </h2>
        <div className="mt-12">{children}</div>
      </div>
    </section>
  );
}
