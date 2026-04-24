"use client";
import { useState } from "react";
import { api, type MonteCarloResponse } from "@/lib/api";
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

const DEFAULT_WAREHOUSES = [
  {
    name: "A",
    initial_stock: 500,
    arrival_rate: 2,
    units_per_order_mean: 1.5,
    units_per_order_std: 0.3,
    service_time_mean: 0.5,
    shipping_mu: 1.0,
    shipping_sigma: 0.4,
    transport_cost_per_unit: 1,
    stockout_penalty_per_unit: 10,
  },
  {
    name: "B",
    initial_stock: 50,
    arrival_rate: 3,
    units_per_order_mean: 1.5,
    units_per_order_std: 0.3,
    service_time_mean: 0.5,
    shipping_mu: 1.2,
    shipping_sigma: 0.6,
    transport_cost_per_unit: 1,
    stockout_penalty_per_unit: 10,
  },
];

export default function SimulatePage() {
  const [horizon, setHorizon] = useState("48");
  const [reps, setReps] = useState("20");
  const [result, setResult] = useState<MonteCarloResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function run() {
    setLoading(true);
    setErr(null);
    setResult(null);
    try {
      const r = await api.simulate.network({
        warehouses: DEFAULT_WAREHOUSES,
        horizon: Number(horizon),
        n_replications: Number(reps),
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
        <h1 className="text-3xl font-semibold tracking-tight">Digital Twin</h1>
        <p className="text-muted-foreground mt-1">
          Monte-Carlo simulation of a two-warehouse fulfillment network (SimPy).
          Use this to validate an optimizer decision before deploying it.
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Run parameters</CardTitle>
          <CardDescription>
            Default: 2 warehouses, A over-stocked, B under-stocked.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4 max-w-md">
            <div className="space-y-2">
              <Label>Horizon (hours)</Label>
              <Input
                value={horizon}
                onChange={(e) => setHorizon(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Replications</Label>
              <Input value={reps} onChange={(e) => setReps(e.target.value)} />
            </div>
          </div>
          <Button variant="accent" onClick={run} disabled={loading}>
            {loading ? "Simulating…" : "Run Monte-Carlo"}
          </Button>
          {err && <div className="text-destructive text-sm">{err}</div>}
        </CardContent>
      </Card>

      {result && (
        <Card>
          <CardHeader>
            <CardTitle>
              Aggregated KPIs ({result.n_replications} reps × {result.horizon}h)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-auto">
              <table className="text-sm w-full">
                <thead className="bg-muted">
                  <tr>
                    <th className="text-left px-3 py-2">KPI</th>
                    <th className="text-right px-3 py-2">mean</th>
                    <th className="text-right px-3 py-2">p5</th>
                    <th className="text-right px-3 py-2">p50</th>
                    <th className="text-right px-3 py-2">p95</th>
                    <th className="text-right px-3 py-2">std</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(result.aggregated).map(([k, v]) => (
                    <tr key={k} className="border-t border-border">
                      <td className="px-3 py-2 font-medium">{k}</td>
                      <td className="px-3 py-2 text-right tabular-nums">
                        {v.mean.toFixed(3)}
                      </td>
                      <td className="px-3 py-2 text-right tabular-nums">
                        {v.p5.toFixed(3)}
                      </td>
                      <td className="px-3 py-2 text-right tabular-nums">
                        {v.p50.toFixed(3)}
                      </td>
                      <td className="px-3 py-2 text-right tabular-nums">
                        {v.p95.toFixed(3)}
                      </td>
                      <td className="px-3 py-2 text-right tabular-nums">
                        {v.std.toFixed(3)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
