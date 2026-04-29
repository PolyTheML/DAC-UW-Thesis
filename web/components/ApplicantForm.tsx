"use client";

import { useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Separator } from "@/components/ui/separator";
import { ChevronDown } from "lucide-react";
import { INPUT_FEATURES, type InputFeature } from "@/config/underwriting-features";

export type FormData = Record<string, number | string | string[]>;

interface ApplicantFormProps {
  onSubmit: (data: FormData) => void;
  disabled?: boolean;
}

function getDefaultValues(): FormData {
  const defaults: FormData = {};
  for (const f of INPUT_FEATURES) {
    switch (f.type) {
      case "continuous":
        defaults[f.name] = Math.round(((f.min ?? 0) + (f.max ?? 100)) / 2);
        break;
      case "binary":
        defaults[f.name] = 0;
        break;
      case "categorical":
        defaults[f.name] = f.options?.[0] ?? "";
        break;
      case "multi_select":
        defaults[f.name] = [];
        break;
    }
  }
  return defaults;
}

export default function ApplicantForm({ onSubmit, disabled }: ApplicantFormProps) {
  const [values, setValues] = useState<FormData>(getDefaultValues());

  const updateValue = useCallback(
    (name: string, value: number | string | string[]) => {
      setValues((prev) => ({ ...prev, [name]: value }));
    },
    []
  );

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      onSubmit(values);
    },
    [values, onSubmit]
  );

  const renderControl = (f: InputFeature) => {
    switch (f.type) {
      case "continuous": {
        const val = Number(values[f.name] ?? 0);
        return (
          <div className="space-y-2" key={f.name}>
            <div className="flex justify-between">
              <Label htmlFor={f.name} className="text-sm font-medium">
                {f.label}
              </Label>
              <span className="text-sm tabular-nums text-muted-foreground">
                {val}
                {f.unit ? ` ${f.unit}` : ""}
              </span>
            </div>
            <Slider
              id={f.name}
              min={f.min}
              max={f.max}
              step={f.step ?? 1}
              value={[val]}
              onValueChange={(v) => updateValue(f.name, Array.isArray(v) ? v[0] : v)}
              disabled={disabled}
            />
            <p className="text-xs text-muted-foreground">{f.description}</p>
          </div>
        );
      }
      case "binary": {
        const checked = Boolean(values[f.name]);
        return (
          <div className="flex items-center justify-between" key={f.name}>
            <div className="space-y-0.5">
              <Label htmlFor={f.name} className="text-sm font-medium">
                {f.label}
              </Label>
              <p className="text-xs text-muted-foreground">{f.description}</p>
            </div>
            <label
              className={`relative inline-flex cursor-pointer items-center ${
                disabled ? "cursor-not-allowed opacity-50" : ""
              }`}
            >
              <input
                id={f.name}
                type="checkbox"
                className="peer sr-only"
                checked={checked}
                onChange={(e) => updateValue(f.name, e.target.checked ? 1 : 0)}
                disabled={disabled}
              />
              <span className="h-5 w-9 rounded-full bg-input transition-colors peer-checked:bg-primary dark:bg-input/80" />
              <span className="absolute left-0.5 top-0.5 block size-4 rounded-full bg-background shadow-sm transition-transform peer-checked:translate-x-4" />
            </label>
          </div>
        );
      }
      case "categorical": {
        const val = String(values[f.name] ?? "");
        return (
          <div className="space-y-2" key={f.name}>
            <Label htmlFor={f.name} className="text-sm font-medium">
              {f.label}
            </Label>
            <div className="relative">
              <select
                id={f.name}
                value={val}
                onChange={(e) => updateValue(f.name, e.target.value)}
                disabled={disabled}
                className="flex h-9 w-full appearance-none items-center justify-between rounded-md border border-input bg-transparent px-3 py-2 pr-8 text-sm shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {f.options?.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
              <ChevronDown className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            </div>
            <p className="text-xs text-muted-foreground">{f.description}</p>
          </div>
        );
      }
      case "multi_select": {
        const selected = Array.isArray(values[f.name])
          ? (values[f.name] as string[])
          : [];
        return (
          <div className="space-y-2" key={f.name}>
            <Label className="text-sm font-medium">{f.label}</Label>
            <div className="flex flex-wrap gap-2">
              {f.options?.map((opt) => {
                const isSelected = selected.includes(opt);
                return (
                  <button
                    key={opt}
                    type="button"
                    disabled={disabled}
                    onClick={() => {
                      const next = isSelected
                        ? selected.filter((s) => s !== opt)
                        : [...selected, opt];
                      updateValue(f.name, next);
                    }}
                    className={`rounded-full border px-3 py-1 text-xs transition-colors ${
                      isSelected
                        ? "border-primary bg-primary text-primary-foreground"
                        : "border-border bg-background text-foreground hover:bg-accent"
                    }`}
                  >
                    {opt}
                  </button>
                );
              })}
            </div>
            <p className="text-xs text-muted-foreground">{f.description}</p>
          </div>
        );
      }
      default:
        return null;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Applicant Profile</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-5">
          {INPUT_FEATURES.map((f, idx) => (
            <div key={f.name}>
              {renderControl(f)}
              {idx < INPUT_FEATURES.length - 1 && <Separator className="mt-5" />}
            </div>
          ))}
          <button
            type="submit"
            disabled={disabled}
            className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            Run Decision
          </button>
        </form>
      </CardContent>
    </Card>
  );
}
