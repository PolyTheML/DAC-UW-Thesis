"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface DecisionPoint {
  round: number;
  reward: number;
  regret: number;
  action: number;
  actionLabel: string;
}

interface LearningChartsProps {
  decisions: DecisionPoint[];
}

function SimpleLineChart({
  data,
  color,
}: {
  data: { x: number; y: number }[];
  color: string;
}) {
  if (data.length === 0) return null;

  const width = 600;
  const height = 200;
  const padding = { top: 10, right: 30, bottom: 30, left: 50 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const minY = Math.min(0, ...data.map((d) => d.y));
  const maxY = Math.max(0, ...data.map((d) => d.y));
  const yRange = maxY - minY || 1;

  const xScale = (i: number) =>
    padding.left + (i / Math.max(data.length - 1, 1)) * chartWidth;
  const yScale = (y: number) =>
    padding.top + chartHeight - ((y - minY) / yRange) * chartHeight;

  const pathD = data
    .map((d, i) => `${i === 0 ? "M" : "L"} ${xScale(i)} ${yScale(d.y)}`)
    .join(" ");

  // Grid lines
  const gridLines = [0, 0.25, 0.5, 0.75, 1].map((t) => {
    const y = padding.top + chartHeight * t;
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
  });

  // Y-axis ticks
  const yTicks = [0, 0.25, 0.5, 0.75, 1].map((t) => {
    const yVal = minY + yRange * (1 - t);
    const y = padding.top + chartHeight * t;
    return (
      <g key={t}>
        <text
          x={padding.left - 8}
          y={y + 4}
          textAnchor="end"
          fontSize={10}
          fill="currentColor"
          fillOpacity={0.6}
        >
          {yVal.toFixed(0)}
        </text>
      </g>
    );
  });

  // X-axis ticks (show first, middle, last)
  const xIndices = [0, Math.floor(data.length / 2), data.length - 1].filter(
    (v, i, a) => a.indexOf(v) === i
  );
  const xTicks = xIndices.map((i) => (
    <text
      key={i}
      x={xScale(i)}
      y={height - padding.bottom + 16}
      textAnchor="middle"
      fontSize={10}
      fill="currentColor"
      fillOpacity={0.6}
    >
      {data[i].x}
    </text>
  ));

  return (
    <div className="h-[200px] w-full">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="h-full w-full"
      >
        {gridLines}
        {yTicks}
        {xTicks}
        <line
          x1={padding.left}
          y1={padding.top}
          x2={padding.left}
          y2={height - padding.bottom}
          stroke="currentColor"
          strokeOpacity={0.2}
        />
        <line
          x1={padding.left}
          y1={height - padding.bottom}
          x2={width - padding.right}
          y2={height - padding.bottom}
          stroke="currentColor"
          strokeOpacity={0.2}
        />
        <path
          d={pathD}
          fill="none"
          stroke={color}
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {data.map((d, i) => (
          <circle
            key={i}
            cx={xScale(i)}
            cy={yScale(d.y)}
            r={3}
            fill={color}
            stroke="white"
            strokeWidth={1}
          />
        ))}
      </svg>
    </div>
  );
}

export default function LearningCharts({ decisions }: LearningChartsProps) {
  const rewardData: { x: number; y: number }[] = [];
  const regretData: { x: number; y: number }[] = [];

  let cumReward = 0;
  let cumRegret = 0;
  for (const d of decisions) {
    cumReward += d.reward;
    cumRegret += d.regret;
    rewardData.push({ x: d.round, y: cumReward });
    regretData.push({ x: d.round, y: cumRegret });
  }

  if (rewardData.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Learning Curves</CardTitle>
        </CardHeader>
        <CardContent className="flex h-48 items-center justify-center text-sm text-muted-foreground">
          Run a few decisions to see cumulative reward and regret over time.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">
          Learning Curves
          <span className="ml-2 text-xs font-normal text-muted-foreground">
            ({rewardData.length} decision{rewardData.length !== 1 ? "s" : ""})
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <div className="mb-2 text-sm font-medium">Cumulative Reward</div>
          <SimpleLineChart data={rewardData} color="#2E5FA3" />
        </div>

        <div>
          <div className="mb-2 text-sm font-medium">Cumulative Regret</div>
          <SimpleLineChart data={regretData} color="#dc2626" />
        </div>
      </CardContent>
    </Card>
  );
}
