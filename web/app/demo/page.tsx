"use client";

import { useState, useCallback } from "react";
import ApplicantForm, { type FormData } from "@/components/ApplicantForm";
import DecisionOutput, { type DecisionData } from "@/components/DecisionOutput";
import LearningCharts from "@/components/LearningCharts";
import PSIMonitor from "@/components/PSIMonitor";
import AlgorithmSelector from "@/components/AlgorithmSelector";
import type { AlgoName } from "@/lib/bandits";
type DemoAlgoName = Exclude<AlgoName, "discountedLinUCB">;

interface DecisionPoint {
  round: number;
  reward: number;
  regret: number;
  action: number;
  actionLabel: string;
}

export default function DemoPage() {
  const [algo, setAlgo] = useState<DemoAlgoName>("linucb");
  const [paramValue, setParamValue] = useState(1.0);
  const [sessionId, setSessionId] = useState<string>("");
  const [latestDecision, setLatestDecision] = useState<DecisionData | null>(null);
  const [decisions, setDecisions] = useState<DecisionPoint[]>([]);
  const [psiData, setPsiData] = useState<Record<string, { value: number; status: string }>>({});
  const [loading, setLoading] = useState(false);

  const handleSubmit = useCallback(
    async (data: FormData) => {
      setLoading(true);
      try {
        const res = await fetch("/api/decide", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            features: data,
            algo,
            sessionId: sessionId || undefined,
            param: paramValue,
          }),
        });
        const json = await res.json();
        if (!res.ok) throw new Error(json.error || "Request failed");

        setSessionId(json.sessionId);

        const decision: DecisionData = {
          action: json.action,
          actionLabel: json.actionLabel,
          riskScore: json.riskScore,
          premiumLoading: json.premiumLoading,
          qValues: json.qValues,
          featureContributions: json.featureContributions,
          reward: json.reward,
          regret: json.regret,
          cumulativeReward: json.cumulativeReward,
          cumulativeRegret: json.cumulativeRegret,
          round: json.round,
        };
        setLatestDecision(decision);
        setDecisions((prev) => [
          ...prev,
          {
            round: json.round,
            reward: json.reward,
            regret: json.regret,
            action: json.action,
            actionLabel: json.actionLabel,
          },
        ]);

        if (json.psi) {
          setPsiData(json.psi);
        }
      } catch (err) {
        console.error(err);
        alert(err instanceof Error ? err.message : "Something went wrong");
      } finally {
        setLoading(false);
      }
    },
    [algo, paramValue, sessionId]
  );

  return (
    <main className="mx-auto max-w-7xl px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Underwriting Demo</h1>
        <p className="text-sm text-muted-foreground">
          Configure an applicant profile, choose an algorithm, and run decisions.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-1">
          <AlgorithmSelector
            algo={algo}
            onAlgoChange={(a) => {
              setAlgo(a);
              setParamValue(
                a === "linucb" ? 1.0 : a === "linTS" ? 1.0 : 0.15
              );
              setSessionId("");
              setDecisions([]);
              setLatestDecision(null);
              setPsiData({});
            }}
            paramValue={paramValue}
            onParamChange={setParamValue}
          />
          <ApplicantForm onSubmit={handleSubmit} disabled={loading} />
        </div>

        <div className="space-y-6 lg:col-span-2">
          <DecisionOutput decision={latestDecision} />

          <LearningCharts decisions={decisions} />

          <PSIMonitor psiData={psiData} />
        </div>
      </div>
    </main>
  );
}
