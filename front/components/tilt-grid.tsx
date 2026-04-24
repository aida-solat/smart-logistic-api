"use client";
import { useRef, type ReactNode } from "react";

/**
 * Grid wrapper that applies a mouse-following 3D tilt to each direct child
 * matching `.tilt-card`, and passes the pointer position as CSS vars
 * `--mx` / `--my` for radial glow effects.
 */
export default function TiltGrid({ children }: { children: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);

  function onMove(e: React.MouseEvent<HTMLDivElement>) {
    const container = ref.current;
    if (!container) return;
    const target = (e.target as HTMLElement).closest<HTMLElement>(".tilt-card");
    if (!target) return;
    const rect = target.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const px = x / rect.width;
    const py = y / rect.height;
    const rotY = (px - 0.5) * 10; // -5 .. +5 deg
    const rotX = (0.5 - py) * 10;
    target.style.setProperty("--mx", `${x}px`);
    target.style.setProperty("--my", `${y}px`);
    target.style.transform = `perspective(1200px) rotateX(${rotX}deg) rotateY(${rotY}deg) translateZ(0)`;
  }

  function onLeave(e: React.MouseEvent<HTMLDivElement>) {
    const target = (e.target as HTMLElement).closest<HTMLElement>(".tilt-card");
    if (!target) return;
    target.style.transform = "";
  }

  return (
    <div
      ref={ref}
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      className="grid md:grid-cols-2 gap-5 [transform-style:preserve-3d]"
    >
      {children}
    </div>
  );
}
