"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ACTIONS, BANDIT_FEATURE_ORDER } from "@/config/underwriting-features";

export interface DecisionData {
  action: number;
  actionLabel: string;
  riskScore: number;
  premiumLoading: number;
  qValues: number[];
  featureContributions: number[];
  reward: number;
  regret: number;
  cumulativeReward: number;
  cumulativeRegret: number;
  round: number;
}

interface DecisionOutputProps {
  decision: DecisionData | null;
}

const badgeVariantMap: Record<string, string> = {
  green: "bg-green-100 text-green-800 border-green-300 dark:bg-green-900 dark:text-green-100",
  amber: "bg-amber-100 text-amber-800 border-amber-300 dark:bg-amber-900 dark:text-amber-100",
  red: "bg-red-100 text-red-800 border-red-300 dark:bg-red-900 dark:text-red-100",
  blue: "bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-900 dark:text-blue-100",
};

export default function DecisionOutput({ decision }: DecisionOutputProps) {
  if (!decision) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-base">Decision Output</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Submit an applicant profile to see the bandit decision.
        </CardContent>
      </Card>
    );
  }

  const actionDef = ACTIONS[decision.action];
  const badgeClass = badgeVariantMap[actionDef.badgeColor] ?? "";

  // Top 5 feature contributions by absolute magnitude
  const topContributions = decision.featureContributions
    .map((value, idx) => ({
      name: BANDIT_FEATURE_ORDER[idx],
      value,
      abs: Math.abs(value),
    }))
    .sort((a, b) => b.abs - a.abs)
    .slice(0, 5);

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-base">
          Decision — Round {decision.round}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-muted-foreground">Action</span>
          <Badge variant="outline" className={badgeClass}>
            {decision.actionLabel}
          </Badge>
          {decision.premiumLoading > 0 && (
            <span className="text-sm text-muted-foreground">
              +{decision.premiumLoading}% loading
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-md border p-3">
            <div className="text-xs text-muted-foreground">Risk Score</div>
            <div className="text-lg font-semibold tabular-nums">
              {decision.riskScore.toFixed(2)}
            </div>
          </div>
          <div className="rounded-md border p-3">
            <div className="text-xs text-muted-foreground">Expected Reward</div>
            <div className="text-lg font-semibold tabular-nums">
              ${decision.reward.toFixed(2)}
            </div>
          </div>
          <div className="rounded-md border p-3">
            <div className="text-xs text-muted-foreground">Regret</div>
            <div className="text-lg font-semibold tabular-nums">
              ${decision.regret.toFixed(2)}
            </div>
          </div>
          <div className="rounded-md border p-3">
            <div className="text-xs text-muted-foreground">Cumulative Reward</div>
            <div className="text-lg font-semibold tabular-nums">
              ${decision.cumulativeReward.toFixed(2)}
            </div>
          </div>
        </div>

        <div>
          <div className="mb-2 text-sm font-medium">Q-Values (per action)</div>
          <div className="space-y-1">
            {decision.qValues.map((q, i) => {
              const isSelected = i === decision.action;
              return (
                <div
                  key={i}
                  className={`flex items-center justify-between rounded px-2 py-1 text-sm ${
                    isSelected ? "bg-muted font-medium" : ""
                  }`}
                >
                  <span>{ACTIONS[i].label}</span>
                  <span className="tabular-nums">{q.toFixed(2)}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div>
          <div className="mb-2 text-sm font-medium">Top Feature Contributions</div>
          <div className="space-y-1">
            {topContributions.map((c) => (
              <div
                key={c.name}
                className="flex items-center justify-between text-sm"
              >
                <span className="text-muted-foreground">{c.name}</span>
                <span
                  className={`tabular-nums ${
                    c.value > 0 ? "text-green-600" : c.value < 0 ? "text-red-600" : ""
                  }`}
                >
                  {c.value > 0 ? "+" : ""}
                  {c.value.toFixed(3)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
