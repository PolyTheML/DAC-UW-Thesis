"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import type { AlgoName } from "@/lib/bandits";

interface AlgorithmSelectorProps {
  algo: Exclude<AlgoName, "discountedLinUCB">;
  onAlgoChange: (algo: Exclude<AlgoName, "discountedLinUCB">) => void;
  paramValue: number;
  onParamChange: (val: number) => void;
}

const ALGO_META: Record<Exclude<AlgoName, "discountedLinUCB">, { label: string; paramLabel: string; min: number; max: number; step: number }> = {
  linucb: { label: "LinUCB", paramLabel: "Alpha (exploration)", min: 0.01, max: 5, step: 0.01 },
  linTS: { label: "Thompson Sampling", paramLabel: "v² (posterior scale)", min: 0.01, max: 5, step: 0.01 },
  epsilonGreedy: { label: "ε-Greedy", paramLabel: "Epsilon", min: 0, max: 1, step: 0.01 },
};

export default function AlgorithmSelector({
  algo,
  onAlgoChange,
  paramValue,
  onParamChange,
}: AlgorithmSelectorProps) {
  const meta = ALGO_META[algo];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Algorithm</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          {(Object.keys(ALGO_META) as Array<keyof typeof ALGO_META>).map((key) => (
            <button
              key={key}
              type="button"
              onClick={() => onAlgoChange(key)}
              className={`rounded-md border px-3 py-1.5 text-sm transition-colors ${
                algo === key
                  ? "border-primary bg-primary text-primary-foreground"
                  : "border-border bg-background text-foreground hover:bg-accent"
              }`}
            >
              {ALGO_META[key].label}
            </button>
          ))}
        </div>

        <div className="space-y-2">
          <div className="flex justify-between">
            <Label className="text-sm">{meta.paramLabel}</Label>
            <span className="text-sm tabular-nums text-muted-foreground">
              {paramValue.toFixed(2)}
            </span>
          </div>
          <Slider
            min={meta.min}
            max={meta.max}
            step={meta.step}
            value={[paramValue]}
            onValueChange={(v) => onParamChange(Array.isArray(v) ? v[0] : v)}
          />
        </div>
      </CardContent>
    </Card>
  );
}
