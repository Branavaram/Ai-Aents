"use client";
import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useRef } from "react";
import type { Agent } from "../lib/api";

export type ChatMsg = {
  agent: string;
  text: string;
  time: string;
};

type Props = {
  messages: ChatMsg[];
  agents: Agent[];
};

export default function ChatPanel({ messages, agents }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const agentMap = Object.fromEntries(agents.map(a => [a.key, a]));

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 h-[500px] flex flex-col">
      <div className="pb-3 border-b border-[var(--border)] flex items-center justify-between">
        <div className="text-xs font-bold tracking-widest text-[var(--text-muted)]">
          💬  #TEAM-CHAT
        </div>
        <div className="text-[10px] text-[var(--text-muted)]">
          {messages.length} msgs
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto mt-3 space-y-3">
        <AnimatePresence initial={false}>
          {messages.map((msg, i) => {
            const a = agentMap[msg.agent];
            if (!a) return null;
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex gap-3"
              >
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center text-xl flex-shrink-0 border-2"
                  style={{
                    background: `${a.color}20`,
                    borderColor: a.color,
                    boxShadow: `0 0 10px ${a.color}40`,
                  }}
                >
                  {a.emoji}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-baseline gap-2 mb-1">
                    <span className="font-bold text-sm" style={{ color: a.color }}>
                      {a.name}
                    </span>
                    <span className="text-[10px] text-[var(--text-muted)] uppercase">
                      {a.role}
                    </span>
                    <span className="text-[10px] text-[var(--text-muted)] ml-auto font-mono">
                      {msg.time}
                    </span>
                  </div>
                  <div className="text-sm text-[var(--text-primary)] leading-relaxed whitespace-pre-wrap break-words">
                    {msg.text}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {messages.length === 0 && (
          <div className="text-center text-[var(--text-muted)] text-sm py-12 italic">
            No messages yet. Run a review to see the team talk.
          </div>
        )}
      </div>
    </div>
  );
}
