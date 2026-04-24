"use client";
import { useState } from "react";
import { api, type CVaRInventoryResponse } from "@/lib/api";
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

export default function OptimizePage() {
  const [initial, setInitial] = useState("100, 20, 60");
  const [mean, setMean] = useState("30, 60, 40");
  const [std, setStd] = useState("5, 15, 8");
  const [alpha, setAlpha] = useState("0.95");
  const [lam, setLam] = useState("0.5");
  const [penalty, setPenalty] = useState("20");
  const [result, setResult] = useState<CVaRInventoryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  function parseNums(s: string) {
    return s
      .split(",")
      .map((x) => Number(x.trim()))
      .filter((x) => !isNaN(x));
  }

  async function run() {
    setLoading(true);
    setErr(null);
    setResult(null);
    try {
      const stock = parseNums(initial);
      const N = stock.length;
      // Uniform transport cost = 1 for now (user can extend later)
      const transport = Array.from({ length: N }, (_, i) =>
        Array.from({ length: N }, (_, j) => (i === j ? 0 : 1)),
      );
      const r = await api.optimize.cvarInventory({
        initial_stock: stock,
        transport_cost: transport,
        demand_mean: parseNums(mean),
        demand_std: parseNums(std),
        alpha: Number(alpha),
        lam: Number(lam),
        stockout_penalty: Number(penalty),
        n_scenarios: 500,
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
          CVaR Inventory
        </h1>
        <p className="text-muted-foreground mt-1">
          Risk-aware reallocation under demand uncertainty
          (Rockafellar-Uryasev).
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Problem setup</CardTitle>
          <CardDescription>
            Comma-separated numbers, one entry per warehouse.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <Field
              label="Initial stock"
              value={initial}
              onChange={setInitial}
            />
            <Field label="Demand mean" value={mean} onChange={setMean} />
            <Field label="Demand std" value={std} onChange={setStd} />
            <Field label="α (tail level)" value={alpha} onChange={setAlpha} />
            <Field label="λ (CVaR weight)" value={lam} onChange={setLam} />
            <Field
              label="Stockout penalty"
              value={penalty}
              onChange={setPenalty}
            />
          </div>
          <Button variant="accent" onClick={run} disabled={loading}>
            {loading ? "Solving…" : "Solve CVaR"}
          </Button>
          {err && <div className="text-destructive text-sm">{err}</div>}
        </CardContent>
      </Card>

      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Solution</CardTitle>
            <CardDescription>Solver: {result.solver_status}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-4 gap-3 text-sm">
              <Stat label="E[loss]" value={result.expected_loss.toFixed(2)} />
              <Stat
                label={`VaR_${result.alpha}`}
                value={result.var_alpha.toFixed(2)}
              />
              <Stat
                label={`CVaR_${result.alpha}`}
                value={result.cvar_alpha.toFixed(2)}
              />
              <Stat label="Objective" value={result.objective.toFixed(2)} />
            </div>

            <div>
              <div className="text-sm font-medium mb-2">
                Reallocation matrix (units moved)
              </div>
              <div className="overflow-auto">
                <table className="text-sm border border-border">
                  <thead className="bg-muted">
                    <tr>
                      <th className="px-2 py-1 border border-border">
                        from \\ to
                      </th>
                      {result.allocation.map((_, j) => (
                        <th key={j} className="px-3 py-1 border border-border">
                          W{j}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.allocation.map((row, i) => (
                      <tr key={i}>
                        <th className="px-2 py-1 border border-border bg-muted">
                          W{i}
                        </th>
                        {row.map((v, j) => (
                          <td
                            key={j}
                            className="px-3 py-1 border border-border text-right tabular-nums"
                          >
                            {v.toFixed(1)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div>
              <div className="text-sm font-medium mb-2">
                Post-reallocation stock
              </div>
              <div className="flex gap-2 flex-wrap">
                {result.post_stock.map((v, i) => (
                  <div
                    key={i}
                    className="rounded-lg border border-border px-3 py-2 text-sm"
                  >
                    <span className="text-muted-foreground">W{i}:</span>{" "}
                    <span className="font-semibold">{v.toFixed(1)}</span>
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
