"use client";

import { useState, useCallback, useEffect } from "react";
import ApplicantForm, { type FormData } from "@/components/ApplicantForm";
import DecisionOutput, { type DecisionData } from "@/components/DecisionOutput";
import LearningCharts from "@/components/LearningCharts";
import PSIMonitor from "@/components/PSIMonitor";
import AlgorithmSelector from "@/components/AlgorithmSelector";
import HumanReviewQueue, { type PendingReview } from "@/components/HumanReviewQueue";
import PolicyAlignmentChart from "@/components/PolicyAlignmentChart";
import type { AlgoName } from "@/lib/bandits";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";

interface DecisionPoint {
  round: number;
  reward: number;
  regret: number;
  action: number;
  actionLabel: string;
}

interface OverrideRecord {
  reviewId: string;
  round: number;
  originalAction: number;
  overrideAction: number;
  overrideLabel: string;
  riskScore: number;
  reward: number;
  regret: number;
  humanName: string;
  timestamp: number;
}

export default function HitlPage() {
  const [algo, setAlgo] = useState<AlgoName>("linucb");
  const [paramValue, setParamValue] = useState(1.0);
  const [sessionId, setSessionId] = useState<string>("");
  const [latestDecision, setLatestDecision] = useState<DecisionData | null>(null);
  const [decisions, setDecisions] = useState<DecisionPoint[]>([]);
  const [psiData, setPsiData] = useState<Record<string, { value: number; status: string }>>({});
  const [loading, setLoading] = useState(false);

  // HITL state
  const [hitlEnabled, setHitlEnabled] = useState(true);
  const [simulatedEnabled, setSimulatedEnabled] = useState(false);
  const [conservatism, setConservatism] = useState(0.5);
  const [pendingReviews, setPendingReviews] = useState<PendingReview[]>([]);
  const [overrideHistory, setOverrideHistory] = useState<OverrideRecord[]>([]);
  const [alignmentScore, setAlignmentScore] = useState(0);
  const [cumulativeHumanCost, setCumulativeHumanCost] = useState(0);
  const [overrideCount, setOverrideCount] = useState(0);

  const fetchSessionState = useCallback(async (sid: string) => {
    try {
      const res = await fetch(`/api/hitl/session?sessionId=${sid}`);
      const json = await res.json();
      if (res.ok) {
        setPendingReviews(json.pendingReviews ?? []);
        setOverrideHistory(json.overrideHistory ?? []);
        setAlignmentScore(json.alignmentScore ?? 0);
        setCumulativeHumanCost(json.cumulativeHumanCost ?? 0);
        setOverrideCount(json.overrideCount ?? 0);
        if (json.psi) setPsiData(json.psi);
      }
    } catch (e) {
      console.error("Failed to fetch session state", e);
    }
  }, []);

  const handleSubmit = useCallback(
    async (data: FormData) => {
      setLoading(true);
      try {
        const res = await fetch("/api/hitl/decide", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            features: data,
            algo,
            sessionId: sessionId || undefined,
            param: paramValue,
            simulatedUnderwriter:
              simulatedEnabled
                ? { enabled: true, conservatism, autoResolveDelayMs: 0 }
                : null,
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

        if (!json.needsHumanReview) {
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
        }

        setPendingReviews((prev) => {
          if (json.needsHumanReview) {
            return [
              ...prev,
              {
                id: `${json.round}-${Date.now()}`,
                round: json.round,
                riskScore: json.riskScore,
                banditRecommendedAction: json.action,
                applicantFeatures: data,
                submittedAt: Date.now(),
              },
            ];
          }
          return prev;
        });

        setOverrideCount(json.overrideCount ?? 0);
        setAlignmentScore(json.alignmentScore ?? 0);
        setCumulativeHumanCost(json.cumulativeHumanCost ?? 0);

        if (json.psi) {
          setPsiData(json.psi);
        }

        // If simulated underwriter is on and there are pending reviews, auto-resolve
        if (simulatedEnabled && json.needsHumanReview) {
          setTimeout(() => {
            handleSimulateAll(json.sessionId);
          }, 300);
        }
      } catch (err) {
        console.error(err);
        alert(err instanceof Error ? err.message : "Something went wrong");
      } finally {
        setLoading(false);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [algo, paramValue, sessionId, simulatedEnabled, conservatism]
  );

  const handleResolve = useCallback(
    async (reviewId: string, action: number) => {
      setLoading(true);
      try {
        const res = await fetch("/api/hitl/review", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            sessionId,
            reviewId,
            overrideAction: action,
            humanName: "user",
          }),
        });
        const json = await res.json();
        if (!res.ok) throw new Error(json.error || "Resolve failed");

        // Update decisions with the resolved override
        setDecisions((prev) => [
          ...prev,
          {
            round: prev.length + overrideCount + 1,
            reward: json.reward,
            regret: json.regret,
            action,
            actionLabel: json.overrideLabel,
          },
        ]);

        setOverrideCount(json.overrideCount ?? 0);
        setAlignmentScore(json.alignmentScore ?? 0);
        setCumulativeHumanCost(json.cumulativeHumanCost ?? 0);
        setPendingReviews((prev) => prev.filter((r) => r.id !== reviewId));

        if (json.psi) {
          setPsiData(json.psi);
        }
      } catch (err) {
        console.error(err);
        alert(err instanceof Error ? err.message : "Resolve failed");
      } finally {
        setLoading(false);
      }
    },
    [sessionId, overrideCount]
  );

  const handleSimulateAll = useCallback(
    async (sid?: string) => {
      const targetSid = sid || sessionId;
      if (!targetSid) return;
      setLoading(true);
      try {
        const res = await fetch("/api/hitl/simulate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ sessionId: targetSid }),
        });
        const json = await res.json();
        if (!res.ok) throw new Error(json.error || "Simulation failed");

        // Refresh full session state
        await fetchSessionState(targetSid);

        // Add synthetic decision markers for resolved items
        if (json.resolvedCount > 0) {
          setDecisions((prev) => {
            const next = [...prev];
            for (let i = 0; i < json.resolvedCount; i++) {
              next.push({
                round: next.length + 1,
                reward: 0,
                regret: 0,
                action: 0,
                actionLabel: "RESOLVED",
              });
            }
            return next;
          });
        }
      } catch (err) {
        console.error(err);
        alert(err instanceof Error ? err.message : "Simulation failed");
      } finally {
        setLoading(false);
      }
    },
    [sessionId, fetchSessionState]
  );

  // Poll for session state when there are pending reviews
  useEffect(() => {
    if (!sessionId || pendingReviews.length === 0) return;
    const interval = setInterval(() => {
      fetchSessionState(sessionId);
    }, 2000);
    return () => clearInterval(interval);
  }, [sessionId, pendingReviews.length, fetchSessionState]);

  return (
    <main className="mx-auto max-w-7xl px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">
          Human-in-the-Loop Underwriting
        </h1>
        <p className="text-sm text-muted-foreground">
          When the bandit selects REFER, a human underwriter reviews and overrides
          the decision. The bandit learns from human feedback.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left column: controls + form */}
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
              setPendingReviews([]);
              setOverrideHistory([]);
              setAlignmentScore(0);
              setCumulativeHumanCost(0);
              setOverrideCount(0);
            }}
            paramValue={paramValue}
            onParamChange={setParamValue}
          />

          {/* HITL Mode Controls */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">HITL Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="hitl-toggle" className="text-sm">
                  Enable Human Review
                </Label>
                <Switch
                  id="hitl-toggle"
                  checked={hitlEnabled}
                  onChange={(e) => setHitlEnabled(e.target.checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="sim-toggle" className="text-sm">
                  Simulated Underwriter
                </Label>
                <Switch
                  id="sim-toggle"
                  checked={simulatedEnabled}
                  onChange={(e) => setSimulatedEnabled(e.target.checked)}
                />
              </div>

              {simulatedEnabled && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Conservatism</span>
                    <span className="text-muted-foreground">
                      {conservatism.toFixed(2)}
                    </span>
                  </div>
                  <Slider
                    min={0}
                    max={1}
                    step={0.05}
                    value={[conservatism]}
                    onValueChange={(v) => setConservatism(Array.isArray(v) ? v[0] : v)}
                  />
                  <p className="text-xs text-muted-foreground">
                    0 = aggressive (close to optimal), 1 = very conservative (declines more)
                  </p>
                </div>
              )}

              {!hitlEnabled && (
                <p className="text-xs text-amber-600">
                  HITL is off — REFER decisions are auto-finalized with the mathematical shortcut.
                </p>
              )}
            </CardContent>
          </Card>

          <ApplicantForm onSubmit={handleSubmit} disabled={loading} />
        </div>

        {/* Right column: outputs */}
        <div className="space-y-6 lg:col-span-2">
          {/* Metrics row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <MetricCard
              label="Queue Depth"
              value={pendingReviews.length.toString()}
              badge={pendingReviews.length > 0 ? "amber" : "green"}
            />
            <MetricCard
              label="Overrides"
              value={overrideCount.toString()}
            />
            <MetricCard
              label="Alignment"
              value={`${(alignmentScore * 100).toFixed(0)}%`}
            />
            <MetricCard
              label="Human Cost"
              value={`$${cumulativeHumanCost}`}
            />
          </div>

          <DecisionOutput decision={latestDecision} />

          <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
            <HumanReviewQueue
              reviews={pendingReviews}
              onResolve={handleResolve}
              onSimulateAll={
                simulatedEnabled ? () => handleSimulateAll() : undefined
              }
              loading={loading}
            />

            <PolicyAlignmentChart
              alignmentScore={alignmentScore}
              overrideHistory={overrideHistory}
            />
          </div>

          <LearningCharts decisions={decisions} />

          <PSIMonitor psiData={psiData} />
        </div>
      </div>
    </main>
  );
}

function MetricCard({
  label,
  value,
  badge,
}: {
  label: string;
  value: string;
  badge?: "green" | "amber" | "red";
}) {
  const badgeClass =
    badge === "green"
      ? "bg-green-100 text-green-800 border-green-300"
      : badge === "amber"
      ? "bg-amber-100 text-amber-800 border-amber-300"
      : badge === "red"
      ? "bg-red-100 text-red-800 border-red-300"
      : undefined;

  return (
    <div className="rounded-lg border p-3">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="mt-1 flex items-center gap-2">
        <span className="text-xl font-semibold tabular-nums">{value}</span>
        {badgeClass && (
          <Badge variant="outline" className={`text-xs ${badgeClass}`}>
            {badge}
          </Badge>
        )}
      </div>
    </div>
  );
}
