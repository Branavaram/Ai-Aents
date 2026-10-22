"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import { Play, Zap, Shield, Bug, BookOpen, FileCode } from "lucide-react";
import OfficeFloor from "./components/OfficeFloor";
import Office3D from "./components/Office3D";
import ChatPanel, { ChatMsg } from "./components/ChatPanel";
import {
  getAgents,
  streamReview,
  type Agent,
  type ReviewMode,
  type StreamEvent,
} from "./lib/api";

type Status = "idle" | "waiting" | "working" | "walking" | "done";

const MODES: { key: ReviewMode; label: string; icon: React.ReactNode; agents: string[] }[] = [
  { key: "full",     label: "Full Review",   icon: <Zap size={16} />,       agents: ["alex","priya","jake","sam","luna"] },
  { key: "bugs",     label: "Bugs Only",     icon: <Bug size={16} />,       agents: ["priya","jake"] },
  { key: "security", label: "Security",      icon: <Shield size={16} />,    agents: ["sam"] },
  { key: "explain",  label: "Explain Code",  icon: <BookOpen size={16} />,  agents: ["luna"] },
];

export default function Home() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [mode, setMode] = useState<ReviewMode>("full");
  const [code, setCode] = useState("");
  const [running, setRunning] = useState(false);
  const [view3D, setView3D] = useState(true);

  const [statuses, setStatuses] = useState<Record<string, Status>>({});
  const [bubbles, setBubbles] = useState<Record<string, string>>({});
  const [walkingTo, setWalkingTo] = useState<Record<string, string>>({});
  const [chat, setChat] = useState<ChatMsg[]>([]);
  const [finalMd, setFinalMd] = useState<string>("");
  const [elapsed, setElapsed] = useState<number>(0);

  useEffect(() => {
    getAgents().then(setAgents).catch(err => console.error("Load agents failed", err));
  }, []);

  const runReview = () => {
    if (!code.trim() || running) return;

    setRunning(true);
    setStatuses({});
    setBubbles({});
    setWalkingTo({});
    setChat([]);
    setFinalMd("");

    const close = streamReview(
      { code, filename: "snippet.py", language: "py", mode },
      (e: StreamEvent) => {
        switch (e.type) {
          case "greeting":
            setStatuses(s => ({ ...s, [e.agent]: "waiting" }));
            setChat(c => [...c, { agent: e.agent, text: e.text, time: e.time }]);
            break;

          case "task_start":
            setStatuses(s => ({ ...s, [e.agent]: "working" }));
            setBubbles(b => ({ ...b, [e.agent]: "💭 Thinking..." }));
            break;

          case "task_done":
            setStatuses(s => ({ ...s, [e.agent]: "done" }));
            setBubbles(b => {
              const next = { ...b };
              delete next[e.agent];
              return next;
            });
            setChat(c => [...c, {
              agent: e.agent,
              text: e.output.slice(0, 500) + (e.output.length > 500 ? "..." : ""),
              time: e.time
            }]);
            break;

          case "walking":
            setStatuses(s => ({ ...s, [e.agent]: "walking" }));
            setWalkingTo(w => ({ ...w, [e.agent]: e.to }));
            setTimeout(() => {
              setWalkingTo(w => {
                const next = { ...w };
                delete next[e.agent];
                return next;
              });
            }, 1500);
            break;

          case "complete":
            setFinalMd(e.final_md);
            setElapsed(e.duration);
            setRunning(false);
            break;

          case "error":
            console.error(e.message);
            setRunning(false);
            break;
        }
      },
      () => setRunning(false)
    );

    // cleanup if user navigates away
    return close;
  };

  const SAMPLE_CODE = `import os, pickle, hashlib

def LoginUser(Username, Password=[]):
    Password.append(Username)
    hashed = hashlib.md5(Password[0].encode()).hexdigest()
    query = f"SELECT * FROM users WHERE name='{Username}' AND pass='{hashed}'"
    try:
        cursor.execute(query)
    except: pass
    return True

def loadProfile(filename):
    return pickle.load(open(filename, "rb"))

def runCmd(cmd):
    os.system("echo " + cmd)
`;

  return (
    <main className="min-h-screen scanlines">
      {/* Header */}
      <header className="border-b border-[var(--border)] bg-[var(--bg-void)]/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[var(--neon-cyan)] to-[var(--neon-pink)] flex items-center justify-center text-xl">
              🤖
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-glow-cyan">
                AI DEV OFFICE
              </h1>
              <div className="text-[10px] text-[var(--text-muted)] tracking-widest">
                MULTI-AGENT CODE REVIEW
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs text-[var(--text-muted)]">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-[var(--neon-green)] pulse-neon" />
              GROQ CONNECTED
            </span>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        {/* View toggle */}
        <div className="flex items-center justify-end gap-2">
          <button
            onClick={() => setView3D(false)}
            className={`px-3 py-1 rounded-md text-xs font-bold tracking-wider border transition-all ${
              !view3D
                ? "border-[var(--neon-cyan)] bg-[var(--neon-cyan)]/10 text-[var(--neon-cyan)]"
                : "border-[var(--border)] text-[var(--text-muted)] hover:border-[var(--border-glow)]"
            }`}
          >
            2D
          </button>
          <button
            onClick={() => setView3D(true)}
            className={`px-3 py-1 rounded-md text-xs font-bold tracking-wider border transition-all ${
              view3D
                ? "border-[var(--neon-pink)] bg-[var(--neon-pink)]/10 text-[var(--neon-pink)]"
                : "border-[var(--border)] text-[var(--text-muted)] hover:border-[var(--border-glow)]"
            }`}
          >
            3D 🎮
          </button>
        </div>

        {/* The office floor */}
        <section>
          {view3D ? (
            <Office3D
              agents={agents}
              statuses={statuses}
              bubbles={bubbles}
              walkingTo={walkingTo}
            />
          ) : (
            <OfficeFloor
              agents={agents}
              statuses={statuses}
              bubbles={bubbles}
              walkingTo={walkingTo}
            />
          )}
        </section>

        {/* Mode selector */}
        <section className="flex flex-wrap gap-2">
          {MODES.map(m => (
            <button
              key={m.key}
              onClick={() => setMode(m.key)}
              className={`px-4 py-2 rounded-lg border flex items-center gap-2 text-sm font-medium transition-all ${
                mode === m.key
                  ? "border-[var(--neon-cyan)] bg-[var(--neon-cyan)]/10 text-[var(--neon-cyan)]"
                  : "border-[var(--border)] text-[var(--text-secondary)] hover:border-[var(--border-glow)]"
              }`}
            >
              {m.icon}
              {m.label}
            </button>
          ))}
        </section>

        {/* Code input + run */}
        <section className="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-6">
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2 text-sm font-medium">
                <FileCode size={16} className="text-[var(--neon-cyan)]" />
                Code to review
              </div>
              <button
                onClick={() => setCode(SAMPLE_CODE)}
                className="text-xs text-[var(--text-muted)] hover:text-[var(--neon-cyan)]"
              >
                Load sample
              </button>
            </div>
            <textarea
              value={code}
              onChange={e => setCode(e.target.value)}
              placeholder="Paste your code here..."
              className="w-full h-64 bg-[var(--bg-void)] border border-[var(--border)] rounded-xl p-4 text-sm font-mono text-[var(--text-primary)] focus:outline-none focus:border-[var(--neon-cyan)] focus:ring-2 focus:ring-[var(--neon-cyan)]/20"
            />
            <motion.button
              onClick={runReview}
              disabled={!code.trim() || running}
              whileHover={{ scale: !code.trim() || running ? 1 : 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`mt-4 w-full py-3 rounded-xl font-bold tracking-wide flex items-center justify-center gap-2 transition-all ${
                !code.trim() || running
                  ? "bg-[var(--border)] text-[var(--text-muted)] cursor-not-allowed"
                  : "bg-gradient-to-r from-[var(--neon-cyan)] to-[var(--neon-pink)] text-black hover:shadow-lg hover:shadow-[var(--neon-cyan)]/50"
              }`}
            >
              <Play size={18} />
              {running ? "TEAM WORKING..." : "LAUNCH REVIEW"}
            </motion.button>
            {elapsed > 0 && !running && (
              <div className="mt-3 text-xs text-[var(--neon-green)] text-center">
                ✓ Completed in {elapsed}s
              </div>
            )}
          </div>

          <ChatPanel messages={chat} agents={agents} />
        </section>

        {/* Final report */}
        {finalMd && (
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-[var(--bg-card)] border border-[var(--neon-cyan)] rounded-2xl p-6"
            style={{ boxShadow: "0 0 30px rgba(0,240,255,0.15)" }}
          >
            <div className="text-xs font-bold tracking-widest text-[var(--neon-cyan)] mb-4">
              📋  FINAL REPORT
            </div>
            <div className="prose prose-invert prose-sm max-w-none">
              <ReactMarkdown>{finalMd}</ReactMarkdown>
            </div>
          </motion.section>
        )}
      </div>
    </main>
  );
}
