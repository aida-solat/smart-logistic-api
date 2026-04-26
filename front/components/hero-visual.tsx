"use client";
import { useEffect, useState } from "react";
import {
  ArrowRight,
  Check,
  GitBranch,
  PackageSearch,
  Sparkles,
} from "lucide-react";

const recommendations = [
  {
    action: "Reallocate 200u",
    detail: "Warehouse A → B",
    uplift: "+89%",
    metric: "service level",
    tone: "emerald",
  },
  {
    action: "Reroute fleet 12",
    detail: "via I-95 corridor",
    uplift: "−18%",
    metric: "tail-risk cost",
    tone: "indigo",
  },
  {
    action: "Hold inventory",
    detail: "SKU-4421 · 7 days",
    uplift: "−81%",
    metric: "stockout risk",
    tone: "indigo",
  },
  {
    action: "Pre-position 50u",
    detail: "Hub-NE · before peak",
    uplift: "+42%",
    metric: "fill rate",
    tone: "emerald",
  },
];

export default function HeroVisual() {
  const [i, setI] = useState(0);
  const [deployed, setDeployed] = useState(false);
  useEffect(() => {
    const t = setInterval(
      () => setI((v) => (v + 1) % recommendations.length),
      3200,
    );
    return () => clearInterval(t);
  }, []);
  const r = recommendations[i];

  function handleApprove() {
    if (deployed) return;
    setDeployed(true);
    setTimeout(() => setDeployed(false), 1800);
  }

  return (
    <div className="relative w-full max-w-[460px] mx-auto">
      {/* Soft glow */}
      <div className="absolute -inset-8 bg-[radial-gradient(ellipse_at_center,rgba(99,91,255,0.18),transparent_70%)] pointer-events-none" />

      {/* Floating card */}
      <div className="relative rounded-2xl border border-zinc-200 bg-white shadow-[0_24px_60px_-20px_rgba(15,23,42,0.18),0_8px_20px_-8px_rgba(99,91,255,0.18)] overflow-hidden hv-float">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-zinc-100">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75 animate-ping" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span className="text-[11px] font-medium text-zinc-700">
              Decision engine
            </span>
            <span className="text-[10px] text-zinc-400">· live</span>
          </div>
          <span className="text-[10px] uppercase tracking-[0.18em] text-zinc-400 font-mono">
            t = {String(i + 1).padStart(2, "0")}
          </span>
        </div>

        {/* Pipeline */}
        <div className="px-5 pt-5 pb-3">
          <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-400 mb-3">
            Causal pipeline
          </div>
          <div className="flex items-center gap-2">
            <Stage icon={GitBranch} label="Observe" delay="0s" />
            <Flow delay="0s" />
            <Stage icon={Sparkles} label="Estimate" delay="0.5s" />
            <Flow delay="3.2s" />
            <Stage icon={PackageSearch} label="Prescribe" delay="1s" active />
          </div>
        </div>

        {/* Sparkline */}
        <div className="px-5 pb-2">
          <Sparkline />
        </div>

        {/* Recommendation */}
        <div className="px-5 py-4 border-t border-zinc-100 bg-gradient-to-b from-white to-zinc-50/60">
          <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-400 mb-2">
            Recommended action
          </div>
          <div
            key={i}
            className="flex items-center justify-between gap-3 hv-fadein"
          >
            <div className="min-w-0">
              <div className="text-sm font-semibold text-zinc-900 truncate">
                {r.action}
              </div>
              <div className="text-xs text-zinc-500 truncate mt-0.5">
                {r.detail}
              </div>
            </div>
            <div className="shrink-0 text-right">
              <div
                className={
                  "text-sm font-bold tabular-nums " +
                  (r.tone === "emerald"
                    ? "text-emerald-600"
                    : "text-indigo-600")
                }
              >
                {r.uplift}
              </div>
              <div className="text-[10px] text-zinc-400 uppercase tracking-wider">
                {r.metric}
              </div>
            </div>
          </div>
          <button
            onClick={handleApprove}
            disabled={deployed}
            className={
              "mt-4 w-full inline-flex items-center justify-center gap-1.5 rounded-md text-xs font-medium px-3 py-2 transition " +
              (deployed
                ? "bg-emerald-500 text-white"
                : "bg-zinc-900 text-white hover:bg-zinc-800")
            }
          >
            {deployed ? (
              <>
                <Check className="h-3.5 w-3.5" strokeWidth={3} />
                Deployed to digital twin
              </>
            ) : (
              <>
                Approve & deploy
                <ArrowRight className="h-3 w-3" />
              </>
            )}
          </button>
        </div>
      </div>

      {/* Floating corner badges — sit outside the card so they never overlap content */}
      <div className="absolute top-40 -left-8 hidden md:block hv-float-slow z-10">
        <div className="rounded-lg bg-white border border-zinc-200 shadow-md px-3 py-2">
          <div className="text-[9px] uppercase tracking-[0.2em] text-zinc-400">
            CVaR₀.₉₅
          </div>
          <div className="text-sm font-semibold text-zinc-900 tabular-nums">
            $ 142k
          </div>
        </div>
      </div>
      <div className="absolute bottom-30 -right-8 hidden md:block hv-float-slower z-10">
        <div className="rounded-lg bg-white border border-zinc-200 shadow-md px-3 py-2">
          <div className="text-[9px] uppercase tracking-[0.2em] text-zinc-400">
            A/B uplift
          </div>
          <div className="text-sm font-semibold text-emerald-600 tabular-nums">
            + 89%
          </div>
        </div>
      </div>
    </div>
  );
}

function Stage({
  icon: Icon,
  label,
  delay,
  active,
}: {
  icon: React.ComponentType<{ className?: string; strokeWidth?: number }>;
  label: string;
  delay: string;
  active?: boolean;
}) {
  return (
    <div className="flex flex-col items-center gap-1.5 flex-1">
      <div
        className={
          "relative h-9 w-9 rounded-lg flex items-center justify-center border " +
          (active
            ? "bg-indigo-50 border-indigo-200"
            : "bg-zinc-50 border-zinc-200")
        }
      >
        <Icon
          className={
            "h-4 w-4 " + (active ? "text-indigo-600" : "text-zinc-500")
          }
          strokeWidth={2}
        />
        {active && (
          <span
            className="absolute inset-0 rounded-lg ring-2 ring-indigo-400/40 animate-pulse"
            style={{ animationDelay: delay }}
          />
        )}
      </div>
      <div className="text-[10px] text-zinc-500 font-medium">{label}</div>
    </div>
  );
}

function Flow({ delay = "0s" }: { delay?: string }) {
  return (
    <div className="flex-1 h-px relative -mt-4 mx-1 overflow-hidden">
      <div className="absolute inset-0 bg-zinc-200" />
      <div
        className="absolute top-0 left-0 h-px w-1/3 bg-gradient-to-r from-transparent via-indigo-500 to-transparent hv-flow"
        style={{ animationDelay: delay }}
      />
    </div>
  );
}

function Sparkline() {
  // Pre-baked path; animates draw-in then breathes
  const d =
    "M0 28 L10 26 L22 22 L34 24 L46 18 L58 20 L70 14 L82 16 L94 10 L108 12 L122 6 L138 8 L154 4";
  return (
    <div className="relative">
      <svg viewBox="0 0 160 36" className="w-full h-9 overflow-visible">
        <defs>
          <linearGradient id="hv-spark" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#635bff" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#635bff" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d={`${d} L154 36 L0 36 Z`} fill="url(#hv-spark)" />
        <path
          d={d}
          fill="none"
          stroke="#635bff"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="hv-spark-draw"
          style={{ strokeDasharray: 400, strokeDashoffset: 400 }}
        />
        <circle cx="154" cy="4" r="3" fill="#635bff">
          <animate
            attributeName="r"
            values="3;4.5;3"
            dur="2s"
            repeatCount="indefinite"
          />
          <animate
            attributeName="opacity"
            values="1;0.5;1"
            dur="2s"
            repeatCount="indefinite"
          />
        </circle>
      </svg>
    </div>
  );
}
