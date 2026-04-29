"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";

interface SeriesPoint {
  round: number;
  cumReward: number;
  cumRegret: number;
  action: number;
}

interface SimulationResult {
  nRounds: number;
  driftRound: number;
  static: { finalReward: number; finalRegret: number; series: SeriesPoint[] };
  adaptive: { finalReward: number; finalRegret: number; series: SeriesPoint[] };
}

export default function DriftPage() {
  const [nRounds, setNRounds] = useState(2000);
  const [driftRound, setDriftRound] = useState(1000);
  const [driftMagnitude, setDriftMagnitude] = useState(1.0);
  const [lambda, setLambda] = useState(0.995);
  const [alpha, setAlpha] = useState(1.0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [animatedIndex, setAnimatedIndex] = useState(0);
  const animRef = useRef<number | null>(null);

  const runSimulation = useCallback(async () => {
    setLoading(true);
    setResult(null);
    setAnimatedIndex(0);
    try {
      const res = await fetch("/api/drift/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nRounds, driftRound, driftMagnitude, lambda, alpha, seed: 42 }),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || "Simulation failed");
      setResult(json);
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Simulation failed");
    } finally {
      setLoading(false);
    }
  }, [nRounds, driftRound, driftMagnitude, lambda, alpha]);

  // Animate the race
  useEffect(() => {
    if (!result) return;
    setAnimatedIndex(0);
    const step = () => {
      setAnimatedIndex((prev) => {
        if (prev >= result.nRounds - 1) {
          if (animRef.current) cancelAnimationFrame(animRef.current);
          return prev;
        }
        animRef.current = requestAnimationFrame(step);
        return prev + Math.max(1, Math.floor(result.nRounds / 300));
      });
    };
    animRef.current = requestAnimationFrame(step);
    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [result]);

  const currentStatic = result?.static.series[Math.min(animatedIndex, result.nRounds - 1)];
  const currentAdaptive = result?.adaptive.series[Math.min(animatedIndex, result.nRounds - 1)];

  return (
    <main className="mx-auto max-w-7xl px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">
          Adaptive Underwriting Under Portfolio Drift
        </h1>
        <p className="text-sm text-muted-foreground">
          Static LinUCB fails when applicant distributions shift. Discounted LinUCB
          (with forgetting factor λ) detects and recovers from drift.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Controls */}
        <div className="space-y-6 lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Simulation Parameters</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              <ParamSlider label="Rounds" value={nRounds} min={500} max={5000} step={500} onChange={setNRounds} />
              <ParamSlider label="Drift Round" value={driftRound} min={100} max={nRounds - 100} step={100} onChange={setDriftRound} />
              <ParamSlider label="Drift Magnitude" value={driftMagnitude} min={0} max={2} step={0.1} onChange={setDriftMagnitude} />
              <ParamSlider label="Alpha (UCB)" value={alpha} min={0.1} max={3} step={0.1} onChange={setAlpha} />
              <ParamSlider label="Lambda (forgetting)" value={lambda} min={0.9} max={1.0} step={0.001} onChange={setLambda} format={(v) => v.toFixed(3)} />

              <Button onClick={runSimulation} disabled={loading} className="w-full">
                {loading ? "Simulating…" : "▶ Run Race"}
              </Button>
            </CardContent>
          </Card>

          {result && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Final Results</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Static LinUCB</span>
                  <span className="font-semibold tabular-nums">${result.static.finalReward.toFixed(0)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Discounted LinUCB</span>
                  <span className="font-semibold tabular-nums text-green-600">${result.adaptive.finalReward.toFixed(0)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Improvement</span>
                  <Badge className="bg-green-100 text-green-800 border-green-300">
                    +{((result.adaptive.finalReward / result.static.finalReward - 1) * 100).toFixed(1)}%
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Regret reduction</span>
                  <Badge className="bg-blue-100 text-blue-800 border-blue-300">
                    {((1 - result.adaptive.finalRegret / result.static.finalRegret) * 100).toFixed(1)}%
                  </Badge>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Visualization */}
        <div className="space-y-6 lg:col-span-2">
          {result && currentStatic && currentAdaptive ? (
            <>
              {/* Race Chart */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center justify-between">
                    <span>Cumulative Reward Race</span>
                    <span className="text-xs font-normal text-muted-foreground">
                      Round {animatedIndex + 1} / {result.nRounds}
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <RaceChart
                    staticSeries={result.static.series}
                    adaptiveSeries={result.adaptive.series}
                    driftRound={result.driftRound}
                    animatedIndex={animatedIndex}
                  />
                </CardContent>
              </Card>

              {/* Regret Chart */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Cumulative Regret</CardTitle>
                </CardHeader>
                <CardContent>
                  <RegretChart
                    staticSeries={result.static.series}
                    adaptiveSeries={result.adaptive.series}
                    driftRound={result.driftRound}
                    animatedIndex={animatedIndex}
                  />
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className="flex h-96 items-center justify-center">
              <CardContent className="text-sm text-muted-foreground text-center">
                {loading ? (
                  <div className="space-y-2">
                    <div className="text-lg">Running simulation…</div>
                    <div className="text-xs">{nRounds.toLocaleString()} rounds, drift at round {driftRound}</div>
                  </div>
                ) : (
                  <div>
                    <div className="text-lg mb-2">Portfolio Drift Simulator</div>
                    <div className="text-xs max-w-md">
                      This demo runs two LinUCB algorithms on the same applicant stream.
                      At the drift round, the population shifts (older, sicker, lower income).
                      The static bandit keeps using outdated parameters. The discounted
                      bandit forgets old data and recovers.
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </main>
  );
}

function ParamSlider({
  label,
  value,
  min,
  max,
  step,
  onChange,
  format,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (v: number) => void;
  format?: (v: number) => string;
}) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <Label>{label}</Label>
        <span className="text-muted-foreground tabular-nums">
          {format ? format(value) : value}
        </span>
      </div>
      <Slider min={min} max={max} step={step} value={[value]} onValueChange={(v) => onChange(Array.isArray(v) ? v[0] : v)} />
    </div>
  );
}

// ── Race Chart (Cumulative Reward) ───────────────────────────────────────────

function RaceChart({
  staticSeries,
  adaptiveSeries,
  driftRound,
  animatedIndex,
}: {
  staticSeries: SeriesPoint[];
  adaptiveSeries: SeriesPoint[];
  driftRound: number;
  animatedIndex: number;
}) {
  const width = 700;
  const height = 280;
  const pad = { top: 20, right: 30, bottom: 40, left: 60 };
  const cw = width - pad.left - pad.right;
  const ch = height - pad.top - pad.bottom;

  const maxReward = Math.max(
    staticSeries[animatedIndex]?.cumReward ?? 0,
    adaptiveSeries[animatedIndex]?.cumReward ?? 0,
    1
  );

  const xScale = (i: number) => pad.left + (i / Math.max(staticSeries.length - 1, 1)) * cw;
  const yScale = (y: number) => pad.top + ch - (y / maxReward) * ch;

  const makePath = (series: SeriesPoint[]) =>
    series
      .slice(0, animatedIndex + 1)
      .map((d, i) => `${i === 0 ? "M" : "L"} ${xScale(i)} ${yScale(d.cumReward)}`)
      .join(" ");

  const driftX = xScale(driftRound - 1);

  return (
    <div className="h-[280px] w-full">
      <svg viewBox={`0 0 ${width} ${height}`} className="h-full w-full">
        {/* Grid */}
        {[0, 0.25, 0.5, 0.75, 1].map((t) => {
          const y = pad.top + ch * (1 - t);
          return (
            <line key={`h-${t}`} x1={pad.left} y1={y} x2={width - pad.right} y2={y} stroke="currentColor" strokeOpacity={0.1} />
          );
        })}
        {/* Drift marker */}
        <line x1={driftX} y1={pad.top} x2={driftX} y2={height - pad.bottom} stroke="#ef4444" strokeDasharray="6 4" strokeWidth={2} />
        <text x={driftX + 4} y={pad.top + 14} fill="#ef4444" fontSize={11} fontWeight={600}>DRIFT</text>
        {/* Paths */}
        <path d={makePath(staticSeries)} fill="none" stroke="#9ca3af" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" />
        <path d={makePath(adaptiveSeries)} fill="none" stroke="#2E5FA3" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" />
        {/* Current dots */}
        {staticSeries[animatedIndex] && (
          <circle cx={xScale(animatedIndex)} cy={yScale(staticSeries[animatedIndex].cumReward)} r={4} fill="#9ca3af" />
        )}
        {adaptiveSeries[animatedIndex] && (
          <circle cx={xScale(animatedIndex)} cy={yScale(adaptiveSeries[animatedIndex].cumReward)} r={4} fill="#2E5FA3" />
        )}
        {/* Axes */}
        <line x1={pad.left} y1={pad.top} x2={pad.left} y2={height - pad.bottom} stroke="currentColor" strokeOpacity={0.2} />
        <line x1={pad.left} y1={height - pad.bottom} x2={width - pad.right} y2={height - pad.bottom} stroke="currentColor" strokeOpacity={0.2} />
        {/* Y ticks */}
        {[0, 0.5, 1].map((t) => {
          const yVal = maxReward * t;
          const y = pad.top + ch * (1 - t);
          return (
            <text key={`yt-${t}`} x={pad.left - 8} y={y + 4} textAnchor="end" fontSize={10} fill="currentColor" fillOpacity={0.6}>
              ${yVal.toFixed(0)}
            </text>
          );
        })}
        {/* X ticks */}
        {[0, Math.floor(staticSeries.length / 2), staticSeries.length - 1].map((i) => (
          <text key={`xt-${i}`} x={xScale(i)} y={height - pad.bottom + 18} textAnchor="middle" fontSize={10} fill="currentColor" fillOpacity={0.6}>
            {staticSeries[i]?.round ?? i}
          </text>
        ))}
        {/* Legend */}
        <g transform={`translate(${width - pad.right - 140}, ${pad.top})`}>
          <line x1={0} y1={0} x2={20} y2={0} stroke="#9ca3af" strokeWidth={2.5} />
          <text x={26} y={4} fontSize={11} fill="currentColor">Static LinUCB</text>
          <line x1={0} y1={16} x2={20} y2={16} stroke="#2E5FA3" strokeWidth={2.5} />
          <text x={26} y={20} fontSize={11} fill="currentColor">Discounted LinUCB</text>
        </g>
      </svg>
    </div>
  );
}

// ── Regret Chart ─────────────────────────────────────────────────────────────

function RegretChart({
  staticSeries,
  adaptiveSeries,
  driftRound,
  animatedIndex,
}: {
  staticSeries: SeriesPoint[];
  adaptiveSeries: SeriesPoint[];
  driftRound: number;
  animatedIndex: number;
}) {
  const width = 700;
  const height = 200;
  const pad = { top: 20, right: 30, bottom: 40, left: 60 };
  const cw = width - pad.left - pad.right;
  const ch = height - pad.top - pad.bottom;

  const maxRegret = Math.max(
    staticSeries[animatedIndex]?.cumRegret ?? 0,
    adaptiveSeries[animatedIndex]?.cumRegret ?? 0,
    1
  );

  const xScale = (i: number) => pad.left + (i / Math.max(staticSeries.length - 1, 1)) * cw;
  const yScale = (y: number) => pad.top + ch - (y / maxRegret) * ch;

  const makePath = (series: SeriesPoint[]) =>
    series
      .slice(0, animatedIndex + 1)
      .map((d, i) => `${i === 0 ? "M" : "L"} ${xScale(i)} ${yScale(d.cumRegret)}`)
      .join(" ");

  const driftX = xScale(driftRound - 1);

  return (
    <div className="h-[200px] w-full">
      <svg viewBox={`0 0 ${width} ${height}`} className="h-full w-full">
        {[0, 0.5, 1].map((t) => {
          const y = pad.top + ch * (1 - t);
          return <line key={`h-${t}`} x1={pad.left} y1={y} x2={width - pad.right} y2={y} stroke="currentColor" strokeOpacity={0.1} />;
        })}
        <line x1={driftX} y1={pad.top} x2={driftX} y2={height - pad.bottom} stroke="#ef4444" strokeDasharray="6 4" strokeWidth={2} />
        <path d={makePath(staticSeries)} fill="none" stroke="#9ca3af" strokeWidth={2} strokeLinecap="round" />
        <path d={makePath(adaptiveSeries)} fill="none" stroke="#dc2626" strokeWidth={2} strokeLinecap="round" />
        <line x1={pad.left} y1={pad.top} x2={pad.left} y2={height - pad.bottom} stroke="currentColor" strokeOpacity={0.2} />
        <line x1={pad.left} y1={height - pad.bottom} x2={width - pad.right} y2={height - pad.bottom} stroke="currentColor" strokeOpacity={0.2} />
        {[0, 0.5, 1].map((t) => {
          const yVal = maxRegret * t;
          const y = pad.top + ch * (1 - t);
          return (
            <text key={`yt-${t}`} x={pad.left - 8} y={y + 4} textAnchor="end" fontSize={10} fill="currentColor" fillOpacity={0.6}>
              ${yVal.toFixed(0)}
            </text>
          );
        })}
        {[0, Math.floor(staticSeries.length / 2), staticSeries.length - 1].map((i) => (
          <text key={`xt-${i}`} x={xScale(i)} y={height - pad.bottom + 18} textAnchor="middle" fontSize={10} fill="currentColor" fillOpacity={0.6}>
            {staticSeries[i]?.round ?? i}
          </text>
        ))}
      </svg>
    </div>
  );
}
