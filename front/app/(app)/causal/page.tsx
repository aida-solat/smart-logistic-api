"use client";
import { useState } from "react";
import { api, type CausalEstimate } from "@/lib/api";
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

export default function CausalPage() {
  const [delta, setDelta] = useState("-2");
  const [sample, setSample] = useState("5000");
  const [result, setResult] = useState<
    | (CausalEstimate & {
        intervention_delta: number;
        expected_outcome_shift: number;
        narrative: string;
      })
    | null
  >(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function run() {
    setLoading(true);
    setErr(null);
    setResult(null);
    try {
      const r = await api.causal.counterfactual({
        intervention_delta: Number(delta),
        sample_size: Number(sample),
        refute: false,
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
        <h1 className="text-3xl font-semibold tracking-tight">Causal Effect</h1>
        <p className="text-muted-foreground mt-1">
          Estimate the causal impact of shortening order-processing time on
          delivery delay. Identifier: DoWhy backdoor adjustment on the Olist
          DAG.
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Counterfactual query</CardTitle>
          <CardDescription>
            If we shift <code>processing_time_days</code> by Δ for every order,
            what happens to <code>delay_days</code>?
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="delta">Intervention Δ (days)</Label>
              <Input
                id="delta"
                value={delta}
                onChange={(e) => setDelta(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sample">Sample size</Label>
              <Input
                id="sample"
                value={sample}
                onChange={(e) => setSample(e.target.value)}
              />
            </div>
          </div>
          <Button onClick={run} disabled={loading} variant="accent">
            {loading ? "Estimating…" : "Estimate effect"}
          </Button>
          {err && <div className="text-destructive text-sm">{err}</div>}
        </CardContent>
      </Card>

      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Result</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-4 text-sm">
              <Stat label="ATE (per day)" value={result.ate.toFixed(4)} />
              <Stat
                label="95% CI"
                value={
                  result.ate_ci_lower != null && result.ate_ci_upper != null
                    ? `[${result.ate_ci_lower.toFixed(3)}, ${result.ate_ci_upper.toFixed(3)}]`
                    : "—"
                }
              />
              <Stat label="n samples" value={String(result.n_samples)} />
              <Stat label="Treatment" value={result.treatment} />
              <Stat label="Outcome" value={result.outcome} />
              <Stat
                label="Δ × ATE"
                value={result.expected_outcome_shift.toFixed(3)}
              />
            </div>
            <div className="rounded-lg border border-border bg-muted/40 p-4 text-sm">
              <div className="font-medium mb-1">Narrative</div>
              {result.narrative}
            </div>
            <div className="text-xs text-muted-foreground">
              Confounders adjusted for: {result.confounders.join(", ")}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border p-3">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="font-semibold mt-1">{value}</div>
    </div>
  );
}
