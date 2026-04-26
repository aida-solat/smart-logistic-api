"use client";
import { useCallback, useEffect, useState } from "react";
import { Sigma, TrendingUp } from "lucide-react";
import {
  CartesianGrid,
  Legend,
  Line,
  ComposedChart,
  ResponsiveContainer,
  Scatter,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api, type CalibrationObservation } from "@/lib/api";
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

type BetaFit = {
  beta: number;
  n_observations: number;
  r_squared: number;
  residual_std: number;
};

export default function CalibrationPage() {
  const [obs, setObs] = useState<CalibrationObservation[]>([]);
  const [fit, setFit] = useState<BetaFit | null>(null);
  const [fitErr, setFitErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const [delay, setDelay] = useState("-1.5");
  const [baseCost, setBaseCost] = useState("1000");
  const [decCost, setDecCost] = useState("550");
  const [note, setNote] = useState("");

  const refresh = useCallback(async () => {
    try {
      const o = await api.calibration.observations();
      setObs(o.observations);
    } catch (e: any) {
      setErr(String(e));
    }
    try {
      const f = await api.calibration.beta();
      setFit(f);
      setFitErr(null);
    } catch (e: any) {
      setFit(null);
      setFitErr(String(e));
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function record() {
    setLoading(true);
    setErr(null);
    try {
      await api.calibration.record({
        delay_shift: Number(delay),
        baseline_cost: Number(baseCost),
        decision_cost: Number(decCost),
        meta: note ? { note } : undefined,
      });
      setNote("");
      await refresh();
    } catch (e: any) {
      setErr(String(e));
    } finally {
      setLoading(false);
    }
  }

  const points = obs.map((o, i) => ({
    idx: i,
    delay_shift: o.delay_shift,
    cost_ratio: o.cost_ratio,
  }));
  const line =
    fit && points.length > 0
      ? (() => {
          const xs = points.map((p) => p.delay_shift);
          const xMin = Math.min(...xs, 0);
          const xMax = Math.max(...xs, 0);
          return [
            { delay_shift: xMin, fit_ratio: 1 + fit.beta * xMin },
            { delay_shift: xMax, fit_ratio: 1 + fit.beta * xMax },
          ];
        })()
      : [];
  const chartData = [...points, ...line].sort(
    (a, b) => a.delay_shift - b.delay_shift,
  );

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight flex items-center gap-3">
          Adaptive β Calibration
        </h1>
        <p className="text-muted-foreground mt-1">
          Log post-deployment outcomes to learn the penalty-sensitivity β used
          by the Informed CVaR pipeline.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard
          title="Current β"
          value={fit ? fit.beta.toFixed(4) : "—"}
          hint={
            fit ? `R² = ${fit.r_squared.toFixed(3)}` : (fitErr ?? "no data")
          }
        />
        <StatCard
          title="Observations"
          value={String(obs.length)}
          hint="appended to log"
        />
        <StatCard
          title="Residual σ"
          value={fit ? fit.residual_std.toFixed(4) : "—"}
          hint="fit noise"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Record new observation
          </CardTitle>
          <CardDescription>
            After deploying an Informed CVaR decision, enter the realized cost
            and the causal delay shift Δ·ATE that was applied.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-4 gap-4">
            <Field
              label="Delay shift (Δ·ATE)"
              value={delay}
              onChange={setDelay}
            />
            <Field
              label="Baseline cost"
              value={baseCost}
              onChange={setBaseCost}
            />
            <Field
              label="Decision cost"
              value={decCost}
              onChange={setDecCost}
            />
            <Field label="Note (optional)" value={note} onChange={setNote} />
          </div>
          <div className="flex items-center gap-3">
            <Button variant="accent" onClick={record} disabled={loading}>
              {loading ? "Saving…" : "Record & refit"}
            </Button>
            <Button variant="outline" onClick={refresh} disabled={loading}>
              Refresh
            </Button>
          </div>
          {err && <div className="text-destructive text-sm">{err}</div>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Observations vs fit</CardTitle>
          <CardDescription>
            Dots are observations; the line is the current fit{" "}
            <code>cost_ratio ≈ 1 + β · delay_shift</code>.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {points.length === 0 ? (
            <div className="text-sm text-muted-foreground">
              No observations yet. Add some above.
            </div>
          ) : (
            <div style={{ width: "100%", height: 340 }}>
              <ResponsiveContainer>
                <ComposedChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="delay_shift"
                    type="number"
                    domain={["dataMin", "dataMax"]}
                    label={{
                      value: "Δ·ATE (days)",
                      position: "insideBottom",
                      offset: -5,
                    }}
                  />
                  <YAxis
                    type="number"
                    domain={["auto", "auto"]}
                    label={{
                      value: "cost ratio",
                      angle: -90,
                      position: "insideLeft",
                    }}
                  />
                  <Tooltip
                    formatter={(v) =>
                      typeof v === "number" ? v.toFixed(3) : String(v ?? "")
                    }
                  />
                  <Legend />
                  <Scatter
                    name="observations"
                    dataKey="cost_ratio"
                    fill="#7c3aed"
                  />
                  <Line
                    type="linear"
                    dataKey="fit_ratio"
                    name="fit: 1 + β·x"
                    stroke="#16a34a"
                    dot={false}
                    strokeWidth={2}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          )}
        </CardContent>
      </Card>

      {obs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Log ({obs.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-auto max-h-80">
              <table className="text-sm w-full">
                <thead className="bg-muted sticky top-0">
                  <tr>
                    <th className="text-left px-3 py-2">#</th>
                    <th className="text-right px-3 py-2">Δ·ATE</th>
                    <th className="text-right px-3 py-2">Baseline</th>
                    <th className="text-right px-3 py-2">Decision</th>
                    <th className="text-right px-3 py-2">Ratio</th>
                    <th className="text-left px-3 py-2">Note</th>
                  </tr>
                </thead>
                <tbody>
                  {obs.map((o, i) => (
                    <tr key={i} className="border-t border-border">
                      <td className="px-3 py-2 text-muted-foreground">
                        {i + 1}
                      </td>
                      <td className="px-3 py-2 text-right tabular-nums">
                        {o.delay_shift.toFixed(3)}
                      </td>
                      <td className="px-3 py-2 text-right tabular-nums">
                        {o.baseline_cost.toFixed(1)}
                      </td>
                      <td className="px-3 py-2 text-right tabular-nums">
                        {o.decision_cost.toFixed(1)}
                      </td>
                      <td className="px-3 py-2 text-right tabular-nums">
                        {o.cost_ratio.toFixed(3)}
                      </td>
                      <td className="px-3 py-2 text-muted-foreground">
                        {typeof o.meta?.note === "string" ? o.meta.note : ""}
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

function StatCard({
  title,
  value,
  hint,
}: {
  title: string;
  value: string;
  hint?: string;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{title}</CardDescription>
        <CardTitle className="text-3xl tabular-nums">{value}</CardTitle>
      </CardHeader>
      {hint && (
        <CardContent className="pt-0 text-xs text-muted-foreground">
          {hint}
        </CardContent>
      )}
    </Card>
  );
}
