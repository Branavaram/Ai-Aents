"use client";
import { AnimatePresence } from "framer-motion";
import type { Agent } from "../lib/api";
import AgentCard from "./AgentCard";

type Status = "idle" | "waiting" | "working" | "walking" | "done";

type Props = {
  agents: Agent[];
  statuses: Record<string, Status>;
  bubbles: Record<string, string>;
  walkingTo: Record<string, string>;   // {priya: "alex"}
};

export default function OfficeFloor({ agents, statuses, bubbles, walkingTo }: Props) {
  const desks = Object.fromEntries(
    agents.map(a => [a.key, { x: a.position, y: a.key === "alex" ? 25 : 65 }])
  );

  return (
    <div className="relative w-full h-[500px] bg-[var(--bg-deep)] rounded-2xl border border-[var(--border)] overflow-hidden grid-bg">
      {/* Title */}
      <div className="absolute top-3 left-1/2 -translate-x-1/2 text-[10px] tracking-[0.4em] font-bold text-[var(--text-muted)]">
        🏢  THE OFFICE FLOOR
      </div>

      {/* Rooms */}
      <div
        className="absolute flex items-center justify-center text-xs text-[var(--text-muted)] border-dashed rounded-xl"
        style={{
          left: "3%", top: "6%", width: "26%", height: "22%",
          background: "rgba(0,240,255,0.03)",
          borderWidth: 1, borderColor: "rgba(0,240,255,0.2)",
        }}
      >
        🪑 Meeting Room
      </div>
      <div
        className="absolute flex items-center justify-center text-xs text-[var(--text-muted)] border-dashed rounded-xl"
        style={{
          right: "3%", top: "6%", width: "22%", height: "22%",
          background: "rgba(255,0,224,0.03)",
          borderWidth: 1, borderColor: "rgba(255,0,224,0.2)",
        }}
      >
        ☕ Coffee
      </div>

      {/* Shared brain */}
      <div
        className="absolute left-1/2 top-[42%] -translate-x-1/2 w-20 h-20 rounded-full flex items-center justify-center pulse-neon"
        style={{
          background: "radial-gradient(circle, rgba(168,85,247,0.3), transparent)",
          border: "2px solid var(--neon-purple)",
          boxShadow: "0 0 25px rgba(168,85,247,0.5)",
        }}
      >
        <span className="text-3xl">🧠</span>
        <div className="absolute -bottom-6 text-[10px] font-bold tracking-widest text-[var(--neon-purple)]">
          SHARED BRAIN
        </div>
      </div>

      {/* Walking paths (SVG) */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        {Object.entries(walkingTo).map(([from, to]) => {
          const src = desks[from];
          const tgt = desks[to];
          if (!src || !tgt) return null;
          const color = agents.find(a => a.key === from)?.color || "#fff";
          return (
            <line
              key={from}
              x1={`${src.x}%`} y1={`${src.y}%`}
              x2={`${tgt.x}%`} y2={`${tgt.y}%`}
              stroke={color} strokeWidth="2"
              strokeDasharray="6,8" opacity="0.6"
            >
              <animate attributeName="stroke-dashoffset"
                from="0" to="28" dur="0.8s" repeatCount="indefinite" />
            </line>
          );
        })}
      </svg>

      {/* Agents */}
      <AnimatePresence>
        {agents.map(agent => {
          const walkingTarget = walkingTo[agent.key];
          const position = walkingTarget && desks[walkingTarget]
            ? { x: desks[walkingTarget].x - 8, y: desks[walkingTarget].y + 5 }
            : desks[agent.key];

          return (
            <AgentCard
              key={agent.key}
              agent={agent}
              status={statuses[agent.key] || "idle"}
              bubble={bubbles[agent.key]}
              position={position}
            />
          );
        })}
      </AnimatePresence>
    </div>
  );
}
