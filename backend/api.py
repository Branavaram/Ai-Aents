"""
FastAPI backend for AI Dev Office.
Exposes: /agents, /knowledge, /reviews, WebSocket /ws/review for live streaming.
"""
import os
import json
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_KEY"] = groq_key or ""
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"

from team import TEAM, get_personality_prompt
from knowledge_loader import load_knowledge_for, list_knowledge_files

BACKEND_DIR = Path(__file__).parent
VAULT = BACKEND_DIR / "vault"

app = FastAPI(title="AI Dev Office API", version="1.0.0")

# CORS — allow Next.js frontend to call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Models ────────────────────────────────────────────────────
class ReviewRequest(BaseModel):
    code: str
    filename: str = "snippet.py"
    language: str = "py"
    mode: str = "full"   # "full" | "bugs" | "security" | "explain"
    model: str = "openai/gpt-oss-120b"


# ─── Helpers ───────────────────────────────────────────────────
def list_past_reviews():
    d = VAULT / "reviews"
    if not d.exists():
        return []
    return sorted(d.glob("*.md"), reverse=True)


def save_review(filename, md, mode):
    d = VAULT / "reviews"
    d.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M")
    safe = filename.replace("/", "_").replace("\\", "_")
    p = d / f"{ts}_[{mode}]_{safe}.md"
    p.write_text(md, encoding="utf-8")
    return p


# ─── REST Endpoints ────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "AI Dev Office API", "version": "1.0.0"}


@app.get("/agents")
def get_agents():
    """List all team members with their profiles."""
    return [
        {
            "key": key,
            "name": t["name"],
            "emoji": t["emoji"],
            "role": t["role"],
            "color": t["color"],
            "position": t["position"],
            "personality": t["personality"],
            "greeting": t["greeting"],
            "signature": t["signature"],
        }
        for key, t in TEAM.items()
    ]


@app.get("/knowledge")
def get_knowledge():
    """List knowledge base files by domain."""
    return list_knowledge_files()


@app.get("/reviews")
def get_reviews(limit: int = 20):
    """List past reviews, newest first."""
    reviews = list_past_reviews()[:limit]
    return [
        {
            "name": r.stem,
            "path": str(r.relative_to(BACKEND_DIR)),
            "modified": r.stat().st_mtime,
        }
        for r in reviews
    ]


@app.get("/reviews/{review_name}")
def get_review_content(review_name: str):
    """Get the markdown content of a specific review."""
    path = VAULT / "reviews" / f"{review_name}.md"
    if not path.exists():
        raise HTTPException(404, "Review not found")
    return {"content": path.read_text(encoding="utf-8")}


# ─── WebSocket for Live Streaming ──────────────────────────────
@app.websocket("/ws/review")
async def websocket_review(ws: WebSocket):
    """
    Stream a code review live. Client sends ReviewRequest, server emits events:
      {"type": "greeting",   "agent": "alex",  "text": "..."}
      {"type": "task_start", "agent": "priya", "task_idx": 0, "total": 5}
      {"type": "task_done",  "agent": "priya", "output": "...", "duration": 12.3}
      {"type": "walking",    "agent": "priya", "to": "alex"}
      {"type": "complete",   "final_md": "...", "duration": 45.1}
      {"type": "error",      "message": "..."}
    """
    await ws.accept()
    try:
        payload = await ws.receive_json()
        req = ReviewRequest(**payload)
        await run_review_stream(ws, req)
    except WebSocketDisconnect:
        return
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass


async def run_review_stream(ws: WebSocket, req: ReviewRequest):
    from crewai import Agent, Task, Crew, LLM

    llm = LLM(
        model=f"openai/{req.model}",
        api_key=groq_key,
        base_url="https://api.groq.com/openai/v1",
        max_tokens=3000,
    )

    agents_in_run = {
        "full":     ["alex", "priya", "jake", "sam", "luna"],
        "bugs":     ["priya", "jake"],
        "security": ["sam"],
        "explain":  ["luna"],
    }.get(req.mode, ["alex"])

    # Greetings
    for key in agents_in_run:
        await ws.send_json({
            "type": "greeting",
            "agent": key,
            "text": TEAM[key]["greeting"],
            "time": datetime.now().strftime("%H:%M:%S"),
        })
        await asyncio.sleep(0.3)

    # Build agents
    def mk(key, goal):
        knowledge = load_knowledge_for(key, max_chars=6000)
        return Agent(
            role=f"{TEAM[key]['role']} named {TEAM[key]['name']}",
            goal=goal,
            backstory=get_personality_prompt(key) + knowledge,
            llm=llm, verbose=False, allow_delegation=False,
        )

    priya = mk("priya", "Review code for bugs & quality.")
    jake  = mk("jake",  "Fresh eyes, ask 'why?'")
    sam   = mk("sam",   "Security audit, OWASP/Bandit.")
    luna  = mk("luna",  "Docs & writing clarity.")
    alex  = mk("alex",  "Combine findings into one PR verdict.")

    agents_map = {"alex": alex, "priya": priya, "jake": jake, "sam": sam, "luna": luna}

    code_block = f"```{req.language}\n{req.code}\n```"
    tasks = []

    if req.mode == "full":
        t_priya = Task(description=f"Review bugs/quality:\n{code_block}", expected_output="Bugs list", agent=priya, context=[])
        t_jake  = Task(description=f"Fresh-eyes:\n{code_block}", expected_output="Confusion", agent=jake, context=[t_priya])
        t_sam   = Task(description=f"Security audit:\n{code_block}", expected_output="Vulns", agent=sam, context=[t_priya])
        t_luna  = Task(description=f"Doc gaps:\n{code_block}", expected_output="Doc issues", agent=luna, context=[t_priya])
        t_alex  = Task(
            description=(
                f"Final PR comment for {req.filename}:\n"
                f"# Code Review — {req.filename}\n\n"
                "## 🚨 Blockers\n## ⚠️ Should Fix\n## 💡 Nice to Have\n"
                "## ✅ Good\n## Verdict\nAPPROVE | REQUEST CHANGES | BLOCK\n\n"
                "Under 300 words."
            ),
            expected_output="Final PR comment", agent=alex,
            context=[t_priya, t_jake, t_sam, t_luna],
        )
        tasks = [t_priya, t_jake, t_sam, t_luna, t_alex]
    elif req.mode == "bugs":
        t = Task(description=f"Bugs in:\n{code_block}", expected_output="Bugs", agent=priya, context=[])
        t2 = Task(description=f"Fresh eyes:\n{code_block}", expected_output="?", agent=jake, context=[t])
        tasks = [t, t2]
    elif req.mode == "security":
        tasks = [Task(description=f"Security:\n{code_block}", expected_output="Vulns", agent=sam, context=[])]
    elif req.mode == "explain":
        tasks = [Task(description=f"Explain:\n{code_block}", expected_output="Walkthrough", agent=luna, context=[])]

    task_outputs = {}
    task_to_key = {}
    for t in tasks:
        for k, a in agents_map.items():
            if t.agent is a:
                task_to_key[id(t)] = k
                break

    start = time.time()
    final_md = ""

    for idx, task in enumerate(tasks):
        key = task_to_key.get(id(task), "alex")
        await ws.send_json({
            "type": "task_start",
            "agent": key,
            "task_idx": idx,
            "total": len(tasks),
            "time": datetime.now().strftime("%H:%M:%S"),
        })

        if not isinstance(task.context, list):
            task.context = []

        # Run the task (blocking) in a thread so WebSocket stays responsive
        task_start = time.time()
        try:
            output = await asyncio.to_thread(task.execute_sync)
            output_text = str(output.raw if hasattr(output, "raw") else output)
        except Exception as e:
            output_text = f"[Error: {e}]"
        task_duration = time.time() - task_start
        task_outputs[id(task)] = output_text

        await ws.send_json({
            "type": "task_done",
            "agent": key,
            "output": output_text,
            "duration": round(task_duration, 1),
            "time": datetime.now().strftime("%H:%M:%S"),
        })

        # Walk to Alex (visual event)
        if key != "alex" and len(agents_in_run) > 1:
            await ws.send_json({"type": "walking", "agent": key, "to": "alex"})
            await asyncio.sleep(0.3)

        final_md = output_text

    total = time.time() - start

    # Save review
    saved = save_review(req.filename, final_md, req.mode)

    await ws.send_json({
        "type": "complete",
        "final_md": final_md,
        "duration": round(total, 1),
        "saved_as": saved.name,
        "time": datetime.now().strftime("%H:%M:%S"),
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
