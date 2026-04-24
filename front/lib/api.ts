// Thin client for the FastAPI backend. Uses Next.js rewrites (/api/* -> backend).

export const API_BASE = "/api";
const TOKEN_KEY = "procint.token";

export const auth = {
  getToken(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(TOKEN_KEY);
  },
  setToken(t: string | null) {
    if (typeof window === "undefined") return;
    if (t) window.localStorage.setItem(TOKEN_KEY, t);
    else window.localStorage.removeItem(TOKEN_KEY);
  },
  async login(role: string = "admin"): Promise<string> {
    const res = await fetch(`${API_BASE}/generate-token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role }),
    });
    if (!res.ok) throw new Error(`Login failed: ${res.status}`);
    const body = (await res.json()) as { access_token: string };
    this.setToken(body.access_token);
    return body.access_token;
  },
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((init?.headers as Record<string, string>) ?? {}),
  };
  const token = auth.getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string }>("/health"),
  causal: {
    graph: () =>
      request<{
        treatment: string;
        outcome: string;
        confounders: string[];
        graph_gml: string;
      }>("/causal/graph"),
    estimate: (body: Record<string, unknown>) =>
      request<CausalEstimate>("/causal/estimate-effect", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    counterfactual: (body: Record<string, unknown>) =>
      request<
        CausalEstimate & {
          intervention_delta: number;
          expected_outcome_shift: number;
          narrative: string;
        }
      >("/causal/counterfactual", {
        method: "POST",
        body: JSON.stringify(body),
      }),
  },
  optimize: {
    cvarInventory: (body: Record<string, unknown>) =>
      request<CVaRInventoryResponse>("/optimize/cvar-inventory", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    cvarOlist: (body: Record<string, unknown>) =>
      request<
        CVaRInventoryResponse & {
          warehouses: string[];
          historical_mean_demand: number[];
          panel_shape: number[];
        }
      >("/optimize/cvar-inventory-olist", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    riskVRP: (body: Record<string, unknown>) =>
      request<RiskVRPResponse>("/optimize/risk-vrp", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    joint: (body: Record<string, unknown>) =>
      request<{
        inventory: CVaRInventoryResponse;
        routing: RiskVRPResponse;
        joint_objective: {
          inventory_cvar: number;
          routing_cvar_makespan: number;
          alpha: number;
        };
      }>("/optimize/joint", { method: "POST", body: JSON.stringify(body) }),
  },
  calibration: {
    record: (body: {
      delay_shift: number;
      baseline_cost: number;
      decision_cost: number;
      meta?: Record<string, unknown>;
    }) =>
      request<{ status: string }>("/causal/calibration/record", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    observations: () =>
      request<{ n: number; observations: CalibrationObservation[] }>(
        "/causal/calibration/observations",
      ),
    beta: () =>
      request<{
        beta: number;
        n_observations: number;
        r_squared: number;
        residual_std: number;
      }>("/causal/calibration/beta"),
  },
  informed: (body: Record<string, unknown>) =>
    request<InformedCVaRResponse>("/causal/informed-cvar", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  feedback: {
    postOverride: (body: OverrideRecord) =>
      request<OverrideRecord>("/feedback/override", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    list: (opts?: { limit?: number; decisionType?: string }) => {
      const q = new URLSearchParams();
      if (opts?.limit) q.set("limit", String(opts.limit));
      if (opts?.decisionType) q.set("decision_type", opts.decisionType);
      const qs = q.toString();
      return request<OverrideRecord[]>(
        `/feedback/overrides${qs ? `?${qs}` : ""}`,
      );
    },
    summary: () => request<OverrideSummary>("/feedback/summary"),
  },
  llm: {
    narrate: (payload: Record<string, unknown>, context?: string) =>
      request<LLMAnswer>("/llm/narrate", {
        method: "POST",
        body: JSON.stringify({ payload, context }),
      }),
    ask: (question: string, payload: Record<string, unknown>) =>
      request<LLMAnswer>("/llm/ask", {
        method: "POST",
        body: JSON.stringify({ question, payload }),
      }),
  },
  simulate: {
    network: (body: Record<string, unknown>) =>
      request<MonteCarloResponse>("/simulate/network", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    validate: (body: Record<string, unknown>) =>
      request<ValidateResponse>("/simulate/validate", {
        method: "POST",
        body: JSON.stringify(body),
      }),
  },
};

export type CalibrationObservation = {
  delay_shift: number;
  baseline_cost: number;
  decision_cost: number;
  cost_ratio: number;
  meta?: Record<string, unknown>;
};

export type InformedCVaRResponse = {
  causal: CausalEstimate & {
    intervention_delta: number;
    expected_outcome_shift: number;
    narrative: string;
  };
  penalty_adjustment: {
    base_stockout_penalty: number;
    beta: number;
    expected_delay_shift: number;
    effective_penalty: number;
    rule: string;
  };
  optimizer: CVaRInventoryResponse;
  warehouses: string[];
  historical_mean_demand: number[];
  panel_shape: number[];
};

export type ValidateResponse = {
  stock_override: Record<string, number>;
  baseline_aggregated: Record<
    string,
    { mean: number; std: number; p5: number; p50: number; p95: number }
  >;
  decision_aggregated: Record<
    string,
    { mean: number; std: number; p5: number; p50: number; p95: number }
  >;
  uplift: Record<
    string,
    { baseline: number; decision: number; absolute: number; relative: number }
  >;
  pareto_improvement: boolean;
  horizon: number;
  n_replications: number;
};

export type CausalEstimate = {
  ate: number;
  ate_ci_lower: number | null;
  ate_ci_upper: number | null;
  refutation_p_value: number | null;
  n_samples: number;
  method: string;
  treatment: string;
  outcome: string;
  confounders: string[];
};

export type CVaRInventoryResponse = {
  allocation: number[][];
  post_stock: number[];
  expected_loss: number;
  cvar_alpha: number;
  var_alpha: number;
  objective: number;
  alpha: number;
  lambda: number;
  n_scenarios: number;
  solver_status: string;
};

export type RiskVRPResponse = {
  routes: { vehicle: number; nodes: number[]; mean_duration: number }[];
  mean_makespan: number;
  cvar_makespan: number;
  var_makespan: number;
  alpha: number;
  n_scenarios: number;
  makespan_samples: number[];
};

export type OverrideRecord = {
  decision_id: string;
  decision_type: string;
  state: Record<string, unknown>;
  ai_recommendation: Record<string, unknown>;
  human_decision: Record<string, unknown>;
  observed_outcome?: Record<string, unknown> | null;
  operator_id?: string | null;
  reason?: string | null;
  created_at?: string;
};

export type OverrideSummary = {
  total: number;
  by_type: Record<string, number>;
  with_outcome: number;
  latest: string | null;
};

export type LLMAnswer = {
  text: string;
  model: string;
  offline: boolean;
};

export type MonteCarloResponse = {
  n_replications: number;
  horizon: number;
  aggregated: Record<
    string,
    { mean: number; std: number; p5: number; p50: number; p95: number }
  >;
  replications: any[];
};
