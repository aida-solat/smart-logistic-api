"use client";
import { useState } from "react";
import { CheckCircle2, XCircle } from "lucide-react";
import {
  BarChart,
  Bar,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api, type ValidateResponse } from "@/lib/api";
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

export default function ValidatePage() {
  const [allocation, setAllocation] = useState("0,200;0,0");
  const [horizon, setHorizon] = useState("48");
  const [reps, setReps] = useState("15");
  const [result, setResult] = useState<ValidateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  function parseAllocation(s: string): number[][] {
    return s.split(";").map((row) =>
      row
        .split(",")
        .map((x) => Number(x.trim()))
        .filter((x) => !isNaN(x)),
    );
  }

  async function run() {
    setLoading(true);
    setErr(null);
    setResult(null);
    try {
      const r = await api.simulate.validate({
        warehouses: DEFAULT_WAREHOUSES,
        allocation: parseAllocation(allocation),
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

  const chartData = result
    ? Object.entries(result.uplift).map(([k, v]) => ({
        kpi: k,
        baseline: v.baseline,
        decision: v.decision,
      }))
    : [];

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight">
          A/B Validation
        </h1>
        <p className="text-muted-foreground mt-1">
          Simulate baseline vs a decision (stock reallocation) in the digital
          twin and measure the uplift on every KPI.
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Parameters</CardTitle>
          <CardDescription>
            Allocation matrix is <code>;</code>-separated rows of <code>,</code>
            -separated numbers (units moved row→column).
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2 col-span-3">
              <Label>Allocation (2×2 for A,B warehouses)</Label>
              <Input
                value={allocation}
                onChange={(e) => setAllocation(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Horizon (h)</Label>
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
            {loading ? "Running A/B…" : "Run A/B simulation"}
          </Button>
          {err && <div className="text-destructive text-sm">{err}</div>}
        </CardContent>
      </Card>

      {result && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {result.pareto_improvement ? (
                  <span className="text-green-600 inline-flex items-center gap-2">
                    <CheckCircle2 className="h-5 w-5" />
                    Pareto improvement
                  </span>
                ) : (
                  <span className="text-destructive inline-flex items-center gap-2">
                    <XCircle className="h-5 w-5" />
                    Not Pareto-improving
                  </span>
                )}
              </CardTitle>
              <CardDescription>
                Stock override: {JSON.stringify(result.stock_override)}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-auto">
                <table className="text-sm w-full">
                  <thead className="bg-muted">
                    <tr>
                      <th className="text-left px-3 py-2">KPI</th>
                      <th className="text-right px-3 py-2">Baseline</th>
                      <th className="text-right px-3 py-2">Decision</th>
                      <th className="text-right px-3 py-2">Δ</th>
                      <th className="text-right px-3 py-2">Δ%</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(result.uplift).map(([k, v]) => (
                      <tr key={k} className="border-t border-border">
                        <td className="px-3 py-2 font-medium">{k}</td>
                        <td className="px-3 py-2 text-right tabular-nums">
                          {v.baseline.toFixed(3)}
                        </td>
                        <td className="px-3 py-2 text-right tabular-nums">
                          {v.decision.toFixed(3)}
                        </td>
                        <td
                          className={`px-3 py-2 text-right tabular-nums ${v.absolute < 0 ? "text-green-600" : v.absolute > 0 ? "text-destructive" : ""}`}
                        >
                          {v.absolute >= 0 ? "+" : ""}
                          {v.absolute.toFixed(3)}
                        </td>
                        <td className="px-3 py-2 text-right tabular-nums">
                          {isFinite(v.relative)
                            ? `${(v.relative * 100).toFixed(1)}%`
                            : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Baseline vs Decision</CardTitle>
              <CardDescription>
                Per-KPI mean over {result.n_replications} replications.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div style={{ width: "100%", height: 320 }}>
                <ResponsiveContainer>
                  <BarChart
                    data={chartData}
                    margin={{ top: 10, right: 20, bottom: 60, left: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="kpi"
                      angle={-35}
                      textAnchor="end"
                      interval={0}
                      height={80}
                    />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="baseline" fill="#94a3b8" />
                    <Bar dataKey="decision" fill="#7c3aed" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
