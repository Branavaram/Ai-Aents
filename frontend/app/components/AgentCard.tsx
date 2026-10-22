"use client";
import { motion } from "framer-motion";
import type { Agent } from "../lib/api";

type Status = "idle" | "waiting" | "working" | "walking" | "done";

type Props = {
  agent: Agent;
  status: Status;
  bubble?: string;
  position: { x: number; y: number };
};

export default function AgentCard({ agent, status, bubble, position }: Props) {
  const glowStyle = status === "working"
    ? { boxShadow: `0 0 20px ${agent.color}, 0 0 40px ${agent.color}60` }
    : status === "done"
    ? { boxShadow: `0 0 15px var(--neon-green)` }
    : status === "walking"
    ? { boxShadow: `0 0 15px ${agent.color}` }
    : {};

  const indicator =
    status === "working" ? { bg: agent.color, icon: "⚡", pulse: true } :
    status === "walking" ? { bg: "#4ab8ff", icon: "🏃", pulse: false } :
    status === "done" ? { bg: "var(--neon-green)", icon: "✓", pulse: false } :
    null;

  return (
    <motion.div
      className="absolute flex flex-col items-center"
      initial={false}
      animate={{ left: `${position.x}%`, top: `${position.y}%` }}
      transition={{ type: "spring", stiffness: 60, damping: 15 }}
      style={{ transform: "translate(-50%, -50%)" }}
    >
      {/* Speech bubble */}
      {bubble && (
        <motion.div
          initial={{ opacity: 0, y: 10, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0 }}
          className="absolute -top-16 bg-[var(--bg-card)] border-2 rounded-xl px-3 py-2 text-xs max-w-[200px] whitespace-nowrap overflow-hidden text-ellipsis"
          style={{
            borderColor: agent.color,
            color: "var(--text-primary)",
            boxShadow: `0 0 15px ${agent.color}40`,
          }}
        >
          {bubble}
          <div
            className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-0 h-0"
            style={{
              borderLeft: "8px solid transparent",
              borderRight: "8px solid transparent",
              borderTop: `10px solid ${agent.color}`,
            }}
          />
        </motion.div>
      )}

      {/* Avatar circle */}
      <motion.div
        className="relative w-16 h-16 rounded-full flex items-center justify-center border-2"
        animate={
          status === "working" ? { y: [0, -6, 0] } :
          status === "walking" ? { rotate: [-3, 3, -3] } :
          {}
        }
        transition={{ duration: 0.6, repeat: Infinity, repeatType: "loop" }}
        style={{
          background: "linear-gradient(135deg, #141428, #0a0a1a)",
          borderColor: status === "idle" ? "var(--border)" : agent.color,
          ...glowStyle,
        }}
      >
        <span className="text-3xl">{agent.emoji}</span>

        {/* Status indicator */}
        {indicator && (
          <div
            className={`absolute -top-1 -right-1 w-6 h-6 rounded-full flex items-center justify-center text-[10px] border-2 border-[var(--bg-void)] ${indicator.pulse ? "pulse-neon" : ""}`}
            style={{ background: indicator.bg }}
          >
            {indicator.icon}
          </div>
        )}

        {/* Sparkles when working */}
        {status === "working" && (
          <>
            {[0, 0.5, 1].map((delay, i) => (
              <motion.span
                key={i}
                className="absolute text-xs pointer-events-none"
                style={{
                  top: ["-10%", "60%", "100%"][i],
                  left: ["-20%", "110%", "40%"][i],
                }}
                animate={{ opacity: [0, 1, 0], y: [0, -8, -16] }}
                transition={{ duration: 1.5, delay, repeat: Infinity }}
              >
                ✨
              </motion.span>
            ))}
          </>
        )}
      </motion.div>

      {/* Name tag */}
      <div
        className="mt-2 text-xs font-bold tracking-wide"
        style={{ color: agent.color }}
      >
        {agent.name}
      </div>
      <div className="text-[10px] text-[var(--text-muted)] uppercase">
        {agent.role}
      </div>
    </motion.div>
  );
}
