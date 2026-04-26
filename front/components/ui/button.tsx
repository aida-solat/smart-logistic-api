"use client";
import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-indigo/60 focus-visible:ring-offset-2 focus-visible:ring-offset-brand-deepest disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "bg-brand-indigo text-brand-deepest shadow-indigo hover:brightness-110 hover:scale-[1.02] active:scale-[0.98]",
        accent:
          "bg-brand-indigo text-brand-deepest shadow-indigo hover:brightness-110 hover:scale-[1.02] active:scale-[0.98]",
        outline:
          "border border-brand-indigo/40 bg-transparent text-brand-cream hover:bg-brand-indigo/10 hover:border-brand-indigo/70",
        ghost:
          "text-brand-cream hover:bg-brand-indigo/10 hover:text-brand-indigo",
        destructive: "bg-destructive text-white hover:brightness-110",
      },
      size: {
        default: "h-10 px-5 py-2",
        sm: "h-8 px-3 text-xs",
        lg: "h-12 px-7 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  },
);

export interface ButtonProps
  extends
    React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";
