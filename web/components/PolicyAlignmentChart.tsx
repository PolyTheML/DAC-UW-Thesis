"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

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

interface PolicyAlignmentChartProps {
  alignmentScore: number;
  overrideHistory: OverrideRecord[];
}

function SimpleBarChart({
  data,
  color,
}: {
  data: { x: number; y: number }[];
  color: string;
}) {
  if (data.length === 0) return null;

  const width = 500;
  const height = 140;
  const padding = { top: 10, right: 20, bottom: 30, left: 40 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const maxY = Math.max(1, ...data.map((d) => d.y));

  const xScale = (i: number) =>
    padding.left + (i / Math.max(data.length - 1, 1)) * chartWidth;

  return (
    <div className="h-[140px] w-full">
      <svg viewBox={`0 0 ${width} ${height}`} className="h-full w-full">
        {/* Grid */}
        {[0, 0.5, 1].map((t) => {
          const y = padding.top + chartHeight * (1 - t);
          return (
            <line
              key={t}
              x1={padding.left}
              y1={y}
              x2={width - padding.right}
              y2={y}
              stroke="currentColor"
              strokeOpacity={0.1}
            />
          );
        })}
        {/* Y ticks */}
        {[0, 0.5, 1].map((t) => {
          const yVal = maxY * t;
          const y = padding.top + chartHeight * (1 - t);
          return (
            <text
              key={t}
              x={padding.left - 6}
              y={y + 4}
              textAnchor="end"
              fontSize={10}
              fill="currentColor"
              fillOpacity={0.6}
            >
              {yVal.toFixed(0)}
            </text>
          );
        })}
        {/* Bars */}
        {data.map((d, i) => {
          const barWidth = Math.max(4, chartWidth / data.length - 2);
          const x = xScale(i) - barWidth / 2;
          const barHeight = (d.y / maxY) * chartHeight;
          const y = padding.top + chartHeight - barHeight;
          return (
            <rect
              key={i}
              x={x}
              y={y}
              width={barWidth}
              height={barHeight}
              fill={color}
              rx={2}
              opacity={0.8}
            />
          );
        })}
        {/* X label */}
        <text
          x={width / 2}
          y={height - 4}
          textAnchor="middle"
          fontSize={10}
          fill="currentColor"
          fillOpacity={0.6}
        >
          Override number
        </text>
      </svg>
    </div>
  );
}

export default function PolicyAlignmentChart({
  alignmentScore,
  overrideHistory,
}: PolicyAlignmentChartProps) {
  const humanCount = overrideHistory.filter((o) => o.humanName === "user").length;
  const simCount = overrideHistory.filter((o) => o.humanName === "simulated").length;

  // Cumulative human cost over overrides
  const costData: { x: number; y: number }[] = [];
  let cumCost = 0;
  for (let i = 0; i < overrideHistory.length; i++) {
    cumCost += 35;
    costData.push({ x: i + 1, y: cumCost });
  }

  // Agreement rate: did bandit already agree with human?
  // Since originalAction is always REFER (3), agreement means human also chose REFER
  // But humans override to 0/1/2, so "agreement" here means the bandit was *directionally* right
  // We'll show a simpler metric: override action distribution
  const actionCounts = [0, 0, 0];
  for (const o of overrideHistory) {
    if (o.overrideAction >= 0 && o.overrideAction <= 2) {
      actionCounts[o.overrideAction]++;
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center justify-between">
          <span>Policy Alignment</span>
          <span className="text-xs font-normal text-muted-foreground">
            {overrideHistory.length} override{overrideHistory.length !== 1 ? "s" : ""}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Alignment score gauge */}
        <div className="rounded-lg border p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Bandit ↔ Human Agreement</span>
            <span className="text-lg font-bold tabular-nums">
              {(alignmentScore * 100).toFixed(0)}%
            </span>
          </div>
          <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${alignmentScore * 100}%`,
                backgroundColor:
                  alignmentScore > 0.7
                    ? "#22c55e"
                    : alignmentScore > 0.4
                    ? "#f59e0b"
                    : "#ef4444",
              }}
            />
          </div>
          <p className="mt-1 text-xs text-muted-foreground">
            Rolling agreement over last 50 overrides. Low = bandit and human disagree often.
          </p>
        </div>

        {/* Override action distribution */}
        <div className="grid grid-cols-3 gap-2">
          <div className="rounded-md border p-2 text-center">
            <div className="text-xs text-muted-foreground">STANDARD</div>
            <div className="text-lg font-semibold text-green-600">{actionCounts[0]}</div>
          </div>
          <div className="rounded-md border p-2 text-center">
            <div className="text-xs text-muted-foreground">RATED</div>
            <div className="text-lg font-semibold text-amber-600">{actionCounts[1]}</div>
          </div>
          <div className="rounded-md border p-2 text-center">
            <div className="text-xs text-muted-foreground">DECLINE</div>
            <div className="text-lg font-semibold text-red-600">{actionCounts[2]}</div>
          </div>
        </div>

        {/* Cost chart */}
        {costData.length > 0 && (
          <div>
            <div className="mb-1 text-sm font-medium">Cumulative Review Cost</div>
            <SimpleBarChart data={costData} color="#2E5FA3" />
          </div>
        )}

        {/* Human vs Simulated breakdown */}
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1">
            <span className="inline-block size-2 rounded-full bg-primary" />
            Human: {humanCount}
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="inline-block size-2 rounded-full bg-muted-foreground" />
            Simulated: {simCount}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
