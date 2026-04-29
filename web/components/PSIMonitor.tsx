"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PSI_REFERENCE } from "@/config/underwriting-features";

interface PSIMonitorProps {
  psiData: Record<string, { value: number; status: string }>;
}

const STATUS_COLORS: Record<string, string> = {
  GREEN: "#16a34a",
  AMBER: "#d97706",
  RED: "#dc2626",
};

function SimpleBarChart({
  data,
}: {
  data: { label: string; value: number; status: string; fill: string }[];
}) {
  if (data.length === 0) return null;

  const width = 600;
  const height = 220;
  const padding = { top: 10, right: 20, bottom: 60, left: 50 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const maxValue = Math.max(0.3, ...data.map((d) => d.value));
  const yScale = (v: number) =>
    padding.top + chartHeight - (v / maxValue) * chartHeight;
  const barWidth = Math.min(60, chartWidth / data.length - 8);
  const barSpacing = chartWidth / data.length;

  return (
    <div className="h-[220px] w-full">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="h-full w-full"
      >
        {/* Grid lines */}
        {[0, 0.1, 0.25, maxValue].map((val, i) => {
          const y = yScale(val);
          return (
            <g key={i}>
              <line
                x1={padding.left}
                y1={y}
                x2={width - padding.right}
                y2={y}
                stroke="currentColor"
                strokeOpacity={0.15}
                strokeDasharray={val === 0.1 || val === 0.25 ? "4 4" : undefined}
              />
              <text
                x={padding.left - 8}
                y={y + 4}
                textAnchor="end"
                fontSize={10}
                fill="currentColor"
                fillOpacity={0.6}
              >
                {val.toFixed(2)}
              </text>
            </g>
          );
        })}

        {/* Y-axis */}
        <line
          x1={padding.left}
          y1={padding.top}
          x2={padding.left}
          y2={height - padding.bottom}
          stroke="currentColor"
          strokeOpacity={0.2}
        />

        {/* X-axis */}
        <line
          x1={padding.left}
          y1={height - padding.bottom}
          x2={width - padding.right}
          y2={height - padding.bottom}
          stroke="currentColor"
          strokeOpacity={0.2}
        />

        {/* Bars */}
        {data.map((d, i) => {
          const x = padding.left + i * barSpacing + (barSpacing - barWidth) / 2;
          const y = yScale(d.value);
          const h = height - padding.bottom - y;
          return (
            <g key={d.label}>
              <rect
                x={x}
                y={y}
                width={barWidth}
                height={Math.max(h, 0)}
                rx={4}
                fill={d.fill}
              />
              <text
                x={x + barWidth / 2}
                y={height - padding.bottom + 16}
                textAnchor="middle"
                fontSize={10}
                fill="currentColor"
                fillOpacity={0.7}
              >
                {d.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

export default function PSIMonitor({ psiData }: PSIMonitorProps) {
  const entries = Object.entries(psiData).map(([feature, data]) => {
    const ref = PSI_REFERENCE[feature];
    const displayName =
      ref?.displayName ??
      feature.charAt(0).toUpperCase() + feature.slice(1);
    return {
      label: displayName,
      value: Number(data.value.toFixed(4)),
      status: data.status,
      fill: STATUS_COLORS[data.status] ?? "#6b7280",
    };
  });

  if (entries.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">PSI Monitor</CardTitle>
        </CardHeader>
        <CardContent className="flex h-48 items-center justify-center text-sm text-muted-foreground">
          Approve applicants (Standard or Rated) to populate the PSI monitor.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">PSI Monitor</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-3 text-xs">
          <div className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-green-600" />
            <span>Stable (&lt;0.10)</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-amber-600" />
            <span>Watch (0.10–0.25)</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-red-600" />
            <span>Alert (&gt;0.25)</span>
          </div>
        </div>

        <SimpleBarChart data={entries} />

        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          {entries.map((e) => (
            <div
              key={e.label}
              className="flex items-center justify-between rounded-md border px-3 py-2"
            >
              <span className="text-sm">{e.label}</span>
              <div className="flex items-center gap-2">
                <span className="text-sm tabular-nums">{e.value.toFixed(4)}</span>
                <Badge
                  variant="outline"
                  className={
                    e.status === "GREEN"
                      ? "border-green-300 text-green-700 dark:text-green-300"
                      : e.status === "AMBER"
                      ? "border-amber-300 text-amber-700 dark:text-amber-300"
                      : "border-red-300 text-red-700 dark:text-red-300"
                  }
                >
                  {e.status}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
