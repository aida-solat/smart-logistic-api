"use client";
import { useState } from "react";
import { Sparkles, ArrowRight, CheckCircle2, XCircle } from "lucide-react";
import { api, type InformedCVaRResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function InformedPage() {
  const [delta, setDelta] = useState("-2");
  const [beta, setBeta] = useState("0.5");
  const [basePenalty, setBasePenalty] = useState("10");
  const [topK, setTopK] = useState("5");
  const [causalSample, setCausalSample] = useState("3000");
  const [result, setResult] = useState<InformedCVaRResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function run() {
    setLoading(true);
    setErr(null);
    setResult(null);
    try {
      const r = await api.informed({
        intervention_delta: Number(delta),
        beta: Number(beta),
        base_stockout_penalty: Number(basePenalty),
        top_k: Number(topK),
        n_scenarios: 300,
        causal_sample_size: Number(causalSample),
      });
      setResult(r);
    } catch (e: any) {
      setErr(String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight flex items-center gap-3">
          <Sparkles className="h-7 w-7 text-accent" />
          Causal-Informed CVaR
        </h1>
        <p className="text-muted-foreground mt-1">
          End-to-end novel pipeline: estimate causal ATE on Olist → adjust
          penalty → solve CVaR on bootstrapped scenarios. Every step is logged
          to MLflow.
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Inputs</CardTitle>
          <CardDescription>
            Δ is the proposed change to <code>processing_time_days</code>
            (negative = faster). β controls how strongly the causal delay shift
            moves the stockout penalty.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <Field
              label="Δ processing time (days)"
              value={delta}
              onChange={setDelta}
            />
            <Field
              label="β penalty sensitivity"
              value={beta}
              onChange={setBeta}
            />
            <Field
              label="Base stockout penalty"
              value={basePenalty}
              onChange={setBasePenalty}
            />
            <Field
              label="top-K warehouses (states)"
              value={topK}
              onChange={setTopK}
            />
            <Field
              label="Causal sample size"
              value={causalSample}
              onChange={setCausalSample}
            />
          </div>
          <Button variant="accent" onClick={run} disabled={loading}>
            {loading ? "Running pipeline…" : "Run pipeline"}
          </Button>
          {err && <div className="text-destructive text-sm">{err}</div>}
        </CardContent>
      </Card>

      {result && (
        <>
          <PipelineFlow result={result} />

          <Card>
            <CardHeader>
              <CardTitle>Step 1 — Causal ATE</CardTitle>
              <CardDescription>
                DoWhy backdoor adjustment on Olist.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-4 gap-3 text-sm">
                <Stat label="ATE" value={result.causal.ate.toFixed(4)} />
                <Stat
                  label="95% CI"
                  value={
                    result.causal.ate_ci_lower != null &&
                    result.causal.ate_ci_upper != null
                      ? `[${result.causal.ate_ci_lower.toFixed(2)}, ${result.causal.ate_ci_upper.toFixed(2)}]`
                      : "—"
                  }
                />
                <Stat
                  label="Δ"
                  value={String(result.causal.intervention_delta)}
                />
                <Stat
                  label="Δ·ATE (days)"
                  value={result.causal.expected_outcome_shift.toFixed(3)}
                />
              </div>
              <div className="mt-4 text-sm rounded-lg border border-border bg-muted/40 p-4">
                {result.causal.narrative}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Step 2 — Penalty adjustment</CardTitle>
              <CardDescription>
                Rule: <code>{result.penalty_adjustment.rule}</code>
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-3 text-sm">
                <Stat
                  label="Base penalty"
                  value={result.penalty_adjustment.base_stockout_penalty.toFixed(
                    2,
                  )}
                />
                <Stat
                  label="β"
                  value={result.penalty_adjustment.beta.toFixed(2)}
                />
                <Stat
                  label="Effective penalty"
                  value={result.penalty_adjustment.effective_penalty.toFixed(3)}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>
                Step 3 — Optimizer (bootstrapped Olist panel)
              </CardTitle>
              <CardDescription>
                Warehouses = top destination states. Panel shape:{" "}
                {result.panel_shape.join(" × ")}.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-4 gap-3 text-sm">
                <Stat
                  label="E[loss]"
                  value={result.optimizer.expected_loss.toFixed(2)}
                />
                <Stat
                  label={`VaR_${result.optimizer.alpha}`}
                  value={result.optimizer.var_alpha.toFixed(2)}
                />
                <Stat
                  label={`CVaR_${result.optimizer.alpha}`}
                  value={result.optimizer.cvar_alpha.toFixed(2)}
                />
                <Stat label="Status" value={result.optimizer.solver_status} />
              </div>

              <div className="text-sm font-medium">Post-reallocation stock</div>
              <div className="flex gap-2 flex-wrap">
                {result.warehouses.map((w, i) => (
                  <div
                    key={w}
                    className="rounded-lg border border-border px-3 py-2 text-sm"
                  >
                    <span className="text-muted-foreground">{w}:</span>{" "}
                    <span className="font-semibold">
                      {result.optimizer.post_stock[i].toFixed(1)}
                    </span>
                    <span className="ml-2 text-xs text-muted-foreground">
                      (hist. μ = {result.historical_mean_demand[i].toFixed(1)})
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}

function PipelineFlow({ result }: { result: InformedCVaRResponse }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Pipeline summary</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-3 text-sm flex-wrap">
          <StepPill
            title="Causal"
            value={`ATE ${result.causal.ate.toFixed(2)}`}
          />
          <ArrowRight className="h-4 w-4 text-muted-foreground" />
          <StepPill
            title="Penalty"
            value={`${result.penalty_adjustment.base_stockout_penalty.toFixed(1)} → ${result.penalty_adjustment.effective_penalty.toFixed(2)}`}
          />
          <ArrowRight className="h-4 w-4 text-muted-foreground" />
          <StepPill
            title="Bootstrap"
            value={`${result.panel_shape[0]} periods`}
          />
          <ArrowRight className="h-4 w-4 text-muted-foreground" />
          <StepPill
            title="CVaR"
            value={`${result.optimizer.cvar_alpha.toFixed(0)}`}
          />
          <div className="ml-3 inline-flex items-center gap-1 text-xs text-green-600">
            <CheckCircle2 className="h-4 w-4" />
            {result.optimizer.solver_status}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function StepPill({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-full border border-border bg-muted px-3 py-1 text-xs">
      <span className="text-muted-foreground">{title}:</span>{" "}
      <span className="font-semibold tabular-nums">{value}</span>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <Input value={value} onChange={(e) => onChange(e.target.value)} />
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border p-3">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="font-semibold mt-1 tabular-nums">{value}</div>
    </div>
  );
}
