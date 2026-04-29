"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export interface PendingReview {
  id: string;
  round: number;
  riskScore: number;
  banditRecommendedAction: number;
  applicantFeatures: Record<string, number | string | string[]>;
  submittedAt: number;
}

interface HumanReviewQueueProps {
  reviews: PendingReview[];
  onResolve: (reviewId: string, action: number) => void;
  onSimulateAll?: () => void;
  loading?: boolean;
}

function FeatureSummary({
  features,
}: {
  features: Record<string, number | string | string[]>;
}) {
  const region = String(features.region ?? "—");
  const occupation = String(features.occupation ?? "—");
  const age = Number(features.age ?? 0);
  const bmi = Number(features.bmi ?? 0);
  const income = Number(features.monthly_income_usd ?? 0);
  const conditions = Array.isArray(features.pre_existing_conditions)
    ? (features.pre_existing_conditions as string[])
    : [];

  return (
    <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-muted-foreground">
      <span>Age {age}, BMI {bmi}</span>
      <span>{region}</span>
      <span>{occupation}</span>
      <span>${income}/mo</span>
      {conditions.length > 0 && (
        <span className="col-span-2 text-amber-600">
          Conditions: {conditions.join(", ")}
        </span>
      )}
      {features.is_smoking ? (
        <span className="col-span-2 text-red-600">Smoker</span>
      ) : null}
    </div>
  );
}

export default function HumanReviewQueue({
  reviews,
  onResolve,
  onSimulateAll,
  loading,
}: HumanReviewQueueProps) {
  if (reviews.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center justify-between">
            <span>Human Review Queue</span>
            <Badge variant="outline" className="text-xs font-normal">
              Empty
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          No cases pending review. When the bandit selects REFER, cases will appear
          here for a human underwriter to resolve.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center justify-between">
          <span>Human Review Queue</span>
          <div className="flex items-center gap-2">
            <Badge className="bg-blue-100 text-blue-800 border-blue-300">
              {reviews.length} pending
            </Badge>
            {onSimulateAll && (
              <Button
                variant="outline"
                size="sm"
                onClick={onSimulateAll}
                disabled={loading}
              >
                Auto-Resolve All
              </Button>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {reviews.map((review) => (
          <div
            key={review.id}
            className="rounded-lg border p-3 space-y-2"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-muted-foreground">
                  Round {review.round}
                </span>
                <Badge variant="outline" className="text-xs">
                  Risk {review.riskScore.toFixed(2)}
                </Badge>
              </div>
              <span className="text-xs text-muted-foreground">
                Bandit chose REFER
              </span>
            </div>

            <FeatureSummary features={review.applicantFeatures} />

            <div className="flex items-center gap-2 pt-1">
              <span className="text-xs text-muted-foreground">Override to:</span>
              <Button
                size="sm"
                variant="outline"
                className="h-7 text-xs border-green-300 text-green-700 hover:bg-green-50"
                onClick={() => onResolve(review.id, 0)}
                disabled={loading}
              >
                STANDARD
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="h-7 text-xs border-amber-300 text-amber-700 hover:bg-amber-50"
                onClick={() => onResolve(review.id, 1)}
                disabled={loading}
              >
                RATED
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="h-7 text-xs border-red-300 text-red-700 hover:bg-red-50"
                onClick={() => onResolve(review.id, 2)}
                disabled={loading}
              >
                DECLINE
              </Button>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
