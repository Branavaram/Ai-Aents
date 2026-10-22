/**
 * API client for the FastAPI backend.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WS_URL = API_URL.replace(/^http/, "ws");

export type Agent = {
  key: string;
  name: string;
  emoji: string;
  role: string;
  color: string;
  position: number;
  personality: string;
  greeting: string;
  signature: string;
};

export type ReviewMode = "full" | "bugs" | "security" | "explain";

export type StreamEvent =
  | { type: "greeting"; agent: string; text: string; time: string }
  | { type: "task_start"; agent: string; task_idx: number; total: number; time: string }
  | { type: "task_done"; agent: string; output: string; duration: number; time: string }
  | { type: "walking"; agent: string; to: string }
  | { type: "complete"; final_md: string; duration: number; saved_as: string; time: string }
  | { type: "error"; message: string };

export async function getAgents(): Promise<Agent[]> {
  const r = await fetch(`${API_URL}/agents`);
  return r.json();
}

export async function getPastReviews(limit = 20) {
  const r = await fetch(`${API_URL}/reviews?limit=${limit}`);
  return r.json();
}

export async function getReviewContent(name: string): Promise<string> {
  const r = await fetch(`${API_URL}/reviews/${encodeURIComponent(name)}`);
  const data = await r.json();
  return data.content;
}

export async function getKnowledge() {
  const r = await fetch(`${API_URL}/knowledge`);
  return r.json();
}

/**
 * Open a WebSocket to stream a code review.
 * Calls onEvent for each event, returns a cleanup function.
 */
export function streamReview(
  payload: { code: string; filename: string; language: string; mode: ReviewMode; model?: string },
  onEvent: (e: StreamEvent) => void,
  onClose?: () => void
): () => void {
  const ws = new WebSocket(`${WS_URL}/ws/review`);

  ws.onopen = () => {
    ws.send(JSON.stringify(payload));
  };

  ws.onmessage = (msg) => {
    try {
      const evt = JSON.parse(msg.data) as StreamEvent;
      onEvent(evt);
    } catch (e) {
      console.error("Bad event:", msg.data);
    }
  };

  ws.onclose = () => {
    onClose?.();
  };

  ws.onerror = (err) => {
    console.error("WebSocket error:", err);
  };

  return () => ws.close();
}
