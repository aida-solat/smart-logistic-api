import * as React from "react";
import { cn } from "@/lib/utils";

export const Input = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(({ className, type, ...props }, ref) => (
  <input
    ref={ref}
    type={type}
    className={cn(
      "flex h-10 w-full rounded-lg border border-brand-gold/20 bg-brand-deepest/60 backdrop-blur-sm px-3.5 py-2 text-sm text-brand-cream placeholder:text-muted-foreground/60 transition-colors focus-visible:outline-none focus-visible:border-brand-gold/60 focus-visible:ring-2 focus-visible:ring-brand-gold/30 disabled:cursor-not-allowed disabled:opacity-50",
      className,
    )}
    {...props}
  />
));
Input.displayName = "Input";
