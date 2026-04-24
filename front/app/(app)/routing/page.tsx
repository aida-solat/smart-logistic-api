"use client";
import { useState } from "react";
import { api, type RiskVRPResponse } from "@/lib/api";
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

// Toy 6-node instance: depot + 5 customers (coords → Euclidean distance).
const DEFAULT_COORDS = [
  [0, 0],
  [2, 1],
  [4, 2],
  [1, 5],
  [5, 5],
  [3, 3],
] as const;
const DEFAULT_DEMANDS = [0, 2, 3, 2, 4, 1];

function distance(a: readonly [number, number], b: readonly [number, number]) {
  const dx = a[0] - b[0];
  const dy = a[1] - b[1];
  return Math.sqrt(dx * dx + dy * dy);
}

function distanceMatrix(coords: readonly (readonly [number, number])[]) {
  return coords.map((a) => coords.map((b) => distance(a, b)));
}

export default function RoutingPage() {
  const [cv, setCv] = useState("0.3");
  const [alpha, setAlpha] = useState("0.95");
  const [capacities, setCapacities] = useState("6, 6");
  const [result, setResult] = useState<RiskVRPResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function run() {
    setLoading(true);
    setErr(null);
    setResult(null);
    try {
      const D = distanceMatrix(DEFAULT_COORDS as any);
      const caps = capacities
        .split(",")
        .map((s) => parseInt(s.trim(), 10))
        .filter((n) => !isNaN(n));
      const r = await api.optimize.riskVRP({
        distance_matrix: D,
        demands: DEFAULT_DEMANDS,
        vehicle_capacities: caps,
        travel_cv: Number(cv),
        n_scenarios: 200,
        alpha: Number(alpha),
        time_limit_s: 5,
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
        <h1 className="text-3xl font-semibold tracking-tight">
          Risk-aware VRP
        </h1>
        <p className="text-muted-foreground mt-1">
          Solve CVRP with OR-Tools, then score makespan CVaR under travel-time
          noise.
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Parameters (toy 5-customer instance)</CardTitle>
          <CardDescription>
            Default coordinates: {JSON.stringify(DEFAULT_COORDS)}. Demands:{" "}
            {DEFAULT_DEMANDS.join(", ")}.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Travel-time CV</Label>
              <Input value={cv} onChange={(e) => setCv(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>α (tail level)</Label>
              <Input value={alpha} onChange={(e) => setAlpha(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>Vehicle capacities</Label>
              <Input
                value={capacities}
                onChange={(e) => setCapacities(e.target.value)}
              />
            </div>
          </div>
          <Button variant="accent" onClick={run} disabled={loading}>
            {loading ? "Solving…" : "Solve VRP + score risk"}
          </Button>
          {err && <div className="text-destructive text-sm">{err}</div>}
        </CardContent>
      </Card>

      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Solution</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-4 gap-3 text-sm">
              <Stat
                label="Mean makespan"
                value={result.mean_makespan.toFixed(3)}
              />
              <Stat
                label={`VaR_${result.alpha}`}
                value={result.var_makespan.toFixed(3)}
              />
              <Stat
                label={`CVaR_${result.alpha}`}
                value={result.cvar_makespan.toFixed(3)}
              />
              <Stat label="Scenarios" value={String(result.n_scenarios)} />
            </div>
            <div>
              <div className="text-sm font-medium mb-2">Routes</div>
              <div className="space-y-2">
                {result.routes.map((r) => (
                  <div
                    key={r.vehicle}
                    className="rounded-lg border border-border p-3 text-sm"
                  >
                    <div className="font-medium">Vehicle {r.vehicle}</div>
                    <div className="text-muted-foreground">
                      depot → {r.nodes.slice(1, -1).join(" → ")} → depot
                      <span className="ml-3">
                        (mean duration:{" "}
                        <span className="tabular-nums">
                          {r.mean_duration.toFixed(2)}
                        </span>
                        )
                      </span>
                    </div>
                  </div>
                ))}
              </div>
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
      <div className="font-semibold mt-1 tabular-nums">{value}</div>
    </div>
  );
}
