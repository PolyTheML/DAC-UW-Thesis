import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col items-center justify-center px-6 py-12 text-center">
      <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
        Adaptive Health Insurance Underwriting
      </h1>
      <p className="mt-2 text-lg text-muted-foreground">
        via Contextual Bandits: A Reinforcement Learning Approach for Cambodia
      </p>

      <Card className="mt-8 w-full text-left">
        <CardContent className="space-y-4 pt-6">
          <p className="text-sm leading-relaxed text-muted-foreground">
            Traditional static underwriting rules are suboptimal for emerging-market
            health insurance because they ignore feature interactions and cannot adapt
            to portfolio drift. This thesis demonstrates how contextual bandits
            (LinUCB and Thompson Sampling) learn optimal accept/rate/decline/refer
            decisions from feedback, while PSI monitors ensure the approved portfolio
            does not drift too far from the actuarial reference.
          </p>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div className="rounded-md border p-3">
              <div className="text-sm font-medium">Dataset</div>
              <div className="text-xs text-muted-foreground">
                2,000 synthetic Cambodia applicants
              </div>
            </div>
            <div className="rounded-md border p-3">
              <div className="text-sm font-medium">Algorithms</div>
              <div className="text-xs text-muted-foreground">
                LinUCB, LinTS, ε-Greedy
              </div>
            </div>
            <div className="rounded-md border p-3">
              <div className="text-sm font-medium">Monitor</div>
              <div className="text-xs text-muted-foreground">
                PSI with GREEN/AMBER/RED thresholds
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="mt-8">
        <Link href="/demo">
          <Button size="lg">Start Demo</Button>
        </Link>
      </div>

      <footer className="mt-12 text-xs text-muted-foreground">
        MSc Thesis — Chanpoly (ITC Cambodia) · Advisor: Has Sothea · DAC
      </footer>
    </main>
  );
}
