import { type LucideIcon } from "lucide-react";
import { type ReactNode } from "react";

export function PageHeader({
  kicker,
  title,
  description,
  icon: Icon,
  actions,
}: {
  kicker?: string;
  title: string;
  description?: ReactNode;
  icon?: LucideIcon;
  actions?: ReactNode;
}) {
  return (
    <header className="relative mb-10">
      <div className="absolute -top-10 left-0 right-0 h-px bg-gradient-to-r from-transparent via-brand-gold/40 to-transparent" />

      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6">
        <div className="flex items-start gap-5">
          {Icon && (
            <div className="orb-chip !w-14 !h-14 !rounded-2xl shrink-0">
              <Icon
                className="h-6 w-6 text-brand-deepest relative z-10"
                strokeWidth={2.2}
              />
            </div>
          )}
          <div>
            {kicker && (
              <div className="text-[11px] uppercase tracking-[0.25em] text-brand-gold">
                {kicker}
              </div>
            )}
            <h1 className="mt-1 font-display text-4xl md:text-5xl tracking-tight text-brand-cream leading-tight">
              {title}
            </h1>
            {description && (
              <p className="mt-3 text-muted-foreground max-w-2xl leading-relaxed">
                {description}
              </p>
            )}
          </div>
        </div>
        {actions && <div className="flex items-center gap-3">{actions}</div>}
      </div>
    </header>
  );
}
