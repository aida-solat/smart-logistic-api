"use client";
import { useState } from "react";
import { api, type LLMAnswer } from "@/lib/api";
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
import { MessageSquare, Sparkles } from "lucide-react";

const EXAMPLE_PAYLOAD = {
  decision_type: "cvar_inventory",
  mean_cost: 123.4,
  cvar_95: 210.7,
  alpha: 0.95,
  allocation: { from_A_to_B: 50, from_C_to_B: 0 },
  post_stock: { A: 150, B: 200, C: 90 },
};

export default function NarratePage() {
  const [payloadText, setPayloadText] = useState(
    JSON.stringify(EXAMPLE_PAYLOAD, null, 2),
  );
  const [context, setContext] = useState("");
  const [question, setQuestion] = useState("Why is the CVaR so much higher than the mean?");
  const [brief, setBrief] = useState<LLMAnswer | null>(null);
  const [answer, setAnswer] = useState<LLMAnswer | null>(null);
  const [loading, setLoading] = useState<"" | "narrate" | "ask">("");
  const [err, setErr] = useState<string | null>(null);

  function parsePayload(): Record<string, unknown> | null {
    try {
      return JSON.parse(payloadText);
    } catch (e) {
      setErr(`Invalid JSON: ${e}`);
      return null;
    }
  }

  async function runNarrate() {
    setErr(null);
    const payload = parsePayload();
    if (!payload) return;
    setLoading("narrate");
    try {
      setBrief(await api.llm.narrate(payload, context || undefined));
    } catch (e: any) {
      setErr(String(e));
    } finally {
      setLoading("");
    }
  }

  async function runAsk() {
    setErr(null);
    const payload = parsePayload();
    if (!payload) return;
    setLoading("ask");
    try {
      setAnswer(await api.llm.ask(question, payload));
    } catch (e: any) {
      setErr(String(e));
    } finally {
      setLoading("");
    }
  }

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight flex items-center gap-3">
          <MessageSquare className="h-7 w-7 text-accent" />
          LLM Narrator & Q&amp;A
        </h1>
        <p className="text-muted-foreground mt-1">
          Turn a decision payload into an executive brief, or ask grounded
          questions about it. Works offline if no <code>OPENAI_API_KEY</code>{" "}
          is set (template fallback).
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Decision payload</CardTitle>
          <CardDescription>
            Paste any optimizer / causal JSON output. The same payload is used
            for both the brief and Q&amp;A.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <textarea
            value={payloadText}
            onChange={(e) => setPayloadText(e.target.value)}
            className="w-full min-h-[200px] rounded-lg border border-border bg-background p-3 font-mono text-xs"
          />
          <div className="space-y-2">
            <Label>Optional context</Label>
            <Input
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="e.g. warehouse B serves a tier-1 SLA region"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-accent" />
            Executive brief
          </CardTitle>
          <CardDescription>
            4-6 sentence summary: recommended action, tail-risk trade-off,
            caveats.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button
            variant="accent"
            onClick={runNarrate}
            disabled={loading === "narrate"}
          >
            {loading === "narrate" ? "Narrating…" : "Generate brief"}
          </Button>
          {brief && <AnswerCard answer={brief} />}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Operator Q&amp;A</CardTitle>
          <CardDescription>
            Answers are grounded strictly in the payload above.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Question</Label>
            <Input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
          </div>
          <Button onClick={runAsk} disabled={loading === "ask"}>
            {loading === "ask" ? "Thinking…" : "Ask"}
          </Button>
          {answer && <AnswerCard answer={answer} />}
        </CardContent>
      </Card>

      {err && <div className="text-destructive text-sm">{err}</div>}
    </div>
  );
}

function AnswerCard({ answer }: { answer: LLMAnswer }) {
  return (
    <div className="rounded-lg border border-border p-4 space-y-2">
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <span
          className={
            "inline-flex h-2 w-2 rounded-full " +
            (answer.offline ? "bg-amber-500" : "bg-emerald-500")
          }
        />
        <span>
          {answer.offline ? "offline template" : "LLM"} · {answer.model}
        </span>
      </div>
      <p className="text-sm whitespace-pre-wrap leading-relaxed">
        {answer.text}
      </p>
    </div>
  );
}
