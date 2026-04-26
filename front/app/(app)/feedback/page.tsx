"use client";
import { useCallback, useEffect, useState } from "react";
import { api, type OverrideRecord, type OverrideSummary } from "@/lib/api";
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
import { UserCog } from "lucide-react";

const DECISION_TYPES = [
  "cvar_inventory",
  "vrp_routing",
  "informed_cvar",
  "joint",
];

const EXAMPLE_STATE = {
  stock: { A: 150, B: 50, C: 90 },
  demand_scenarios: "500x3 bootstrap",
};
const EXAMPLE_AI = { move_from_A_to_B: 50 };
const EXAMPLE_HUMAN = { move_from_A_to_B: 20 };

export default function FeedbackPage() {
  const [decisionId, setDecisionId] = useState("dec-" + Date.now());
  const [decisionType, setDecisionType] = useState("cvar_inventory");
  const [stateText, setStateText] = useState(
    JSON.stringify(EXAMPLE_STATE, null, 2),
  );
  const [aiText, setAiText] = useState(JSON.stringify(EXAMPLE_AI, null, 2));
  const [humanText, setHumanText] = useState(
    JSON.stringify(EXAMPLE_HUMAN, null, 2),
  );
  const [reason, setReason] = useState("");
  const [operator, setOperator] = useState("");

  const [summary, setSummary] = useState<OverrideSummary | null>(null);
  const [records, setRecords] = useState<OverrideRecord[]>([]);
  const [filterType, setFilterType] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [s, list] = await Promise.all([
        api.feedback.summary(),
        api.feedback.list({
          limit: 20,
          decisionType: filterType || undefined,
        }),
      ]);
      setSummary(s);
      setRecords(list);
    } catch (e: any) {
      setErr(String(e));
    }
  }, [filterType]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function submit() {
    setErr(null);
    setLoading(true);
    try {
      const body = {
        decision_id: decisionId,
        decision_type: decisionType,
        state: JSON.parse(stateText),
        ai_recommendation: JSON.parse(aiText),
        human_decision: JSON.parse(humanText),
        reason: reason || undefined,
        operator_id: operator || undefined,
      };
      await api.feedback.postOverride(body as OverrideRecord);
      setDecisionId("dec-" + Date.now());
      setReason("");
      await refresh();
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
          Operator Feedback Loop
        </h1>
        <p className="text-muted-foreground mt-1">
          Log human overrides of AI recommendations. These tuples are the
          counterfactual training signal for active-learning retraining.
        </p>
      </header>

      <div className="grid sm:grid-cols-4 gap-4">
        <Stat label="Total overrides" value={summary?.total ?? "—"} />
        <Stat label="With outcome" value={summary?.with_outcome ?? "—"} />
        <Stat
          label="Decision types"
          value={summary ? Object.keys(summary.by_type).length : "—"}
        />
        <Stat
          label="Latest"
          value={
            summary?.latest ? new Date(summary.latest).toLocaleString() : "—"
          }
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Log an override</CardTitle>
          <CardDescription>
            State / AI / Human fields accept arbitrary JSON.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid sm:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Decision ID</Label>
              <Input
                value={decisionId}
                onChange={(e) => setDecisionId(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Decision type</Label>
              <select
                value={decisionType}
                onChange={(e) => setDecisionType(e.target.value)}
                className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm"
              >
                {DECISION_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label>Operator ID</Label>
              <Input
                value={operator}
                onChange={(e) => setOperator(e.target.value)}
                placeholder="optional"
              />
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-4">
            <JsonField
              label="State"
              value={stateText}
              onChange={setStateText}
            />
            <JsonField
              label="AI recommendation"
              value={aiText}
              onChange={setAiText}
            />
            <JsonField
              label="Human decision"
              value={humanText}
              onChange={setHumanText}
            />
          </div>

          <div className="space-y-2">
            <Label>Reason</Label>
            <Input
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="why did you override the recommendation?"
            />
          </div>

          <Button variant="accent" onClick={submit} disabled={loading}>
            {loading ? "Submitting…" : "Submit override"}
          </Button>
          {err && <div className="text-destructive text-sm">{err}</div>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-4">
          <div>
            <CardTitle>Recent overrides</CardTitle>
            <CardDescription>Newest first. Up to 20 shown.</CardDescription>
          </div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="h-9 rounded-lg border border-border bg-background px-3 text-xs"
          >
            <option value="">all types</option>
            {DECISION_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </CardHeader>
        <CardContent>
          {records.length === 0 ? (
            <div className="text-sm text-muted-foreground">
              No overrides yet.
            </div>
          ) : (
            <div className="space-y-2">
              {records.map((r) => (
                <div
                  key={r.decision_id + (r.created_at ?? "")}
                  className="rounded-lg border border-border p-3 text-sm space-y-1"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="font-medium">{r.decision_id}</div>
                    <div className="text-xs text-muted-foreground">
                      {r.decision_type}
                      {r.created_at
                        ? " · " + new Date(r.created_at).toLocaleString()
                        : ""}
                    </div>
                  </div>
                  {r.reason && (
                    <div className="text-muted-foreground">“{r.reason}”</div>
                  )}
                  <div className="grid md:grid-cols-2 gap-2 text-xs font-mono text-muted-foreground">
                    <div>AI: {JSON.stringify(r.ai_recommendation)}</div>
                    <div>Human: {JSON.stringify(r.human_decision)}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-border p-3">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="font-semibold mt-1 tabular-nums">{String(value)}</div>
    </div>
  );
}

function JsonField({
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
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full min-h-[140px] rounded-lg border border-border bg-background p-3 font-mono text-xs"
      />
    </div>
  );
}
