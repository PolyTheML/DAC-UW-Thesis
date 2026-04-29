"use client"

import * as React from "react"

import { cn } from "@/lib/utils"

const Switch = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement> & { size?: "sm" | "default" }>(
  ({ className, size = "default", ...props }, ref) => {
    return (
      <label
        className={cn(
          "relative inline-flex cursor-pointer items-center",
          size === "default" ? "h-[20px] w-[36px]" : "h-[16px] w-[28px]",
          className
        )}
      >
        <input
          type="checkbox"
          className="peer sr-only"
          ref={ref}
          {...props}
        />
        <span
          className={cn(
            "absolute inset-0 rounded-full border border-transparent bg-input transition-colors peer-focus-visible:ring-2 peer-focus-visible:ring-ring peer-focus-visible:ring-offset-2 peer-focus-visible:ring-offset-background peer-disabled:cursor-not-allowed peer-disabled:opacity-50 dark:bg-input/80",
            "peer-checked:bg-primary"
          )}
        />
        <span
          className={cn(
            "absolute block rounded-full bg-background shadow-sm transition-transform",
            size === "default" ? "size-4" : "size-3",
            "left-[2px] peer-checked:translate-x-[calc(100%-2px)]"
          )}
        />
      </label>
    )
  }
)
Switch.displayName = "Switch"

export { Switch }
