"""
AI Dev Team Office — Streamlit UI
5 agents with personalities, animated office, Slack chat
Run with:  streamlit run app.py
"""
import os
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

from agent_office import render_office
from chat_panel import render_chat
from office_world import render_office_world, DESKS
from timeline import render_timeline
from team import TEAM, get_personality_prompt
from knowledge_loader import load_knowledge_for, list_knowledge_files

# ─── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="AI Dev Team", page_icon="🏢", layout="wide")

# ─── Env ──────────────────────────────────────────────────────
load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_KEY"] = groq_key or ""
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"

VAULT = Path(__file__).parent / "vault"

# ─── Vault helpers ────────────────────────────────────────────
def load_vault_knowledge():
    out = []
    for folder in ["profile", "knowledge", "projects"]:
        f = VAULT / folder
        if f.exists():
            for md in f.glob("*.md"):
                out.append(f"### {folder}/{md.name}\n{md.read_text(encoding='utf-8', errors='replace')}")
    return "\n---\n".join(out) if out else "(empty)"

def save_review(filename, md, mode):
    d = VAULT / "reviews"; d.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M")
    safe = filename.replace("/", "_").replace("\\", "_")
    p = d / f"{ts}_[{mode}]_{safe}.md"
    p.write_text(md, encoding="utf-8")
    return p

def list_past_reviews():
    d = VAULT / "reviews"
    return sorted(d.glob("*.md"), reverse=True) if d.exists() else []

# ─── Session state ────────────────────────────────────────────
if "selected_review" not in st.session_state:
    st.session_state.selected_review = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "timeline_events" not in st.session_state:
    st.session_state.timeline_events = []
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None

# ─── Header ───────────────────────────────────────────────────
st.markdown("# 🏢 AI Dev Team Office")
st.caption("Watch 5 AI teammates review your code together — each with their own personality")
st.divider()

# ─── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.header("👥 Meet the Team")
    for key, t in TEAM.items():
        if st.button(
            f"{t['emoji']} {t['name']} · {t['role']}",
            key=f"team_{key}",
            use_container_width=True,
        ):
            st.session_state.selected_agent = key
            st.rerun()

    st.divider()
    model_choice = st.selectbox("Model", ["openai/gpt-oss-120b", "openai/gpt-oss-20b"], index=0)
    max_chars = st.slider("Max chars", 2000, 15000, 6000, 1000)
    use_vault = st.toggle("🧠 Use vault memory", value=True)

    st.divider()
    st.header("📜 History")
    past = list_past_reviews()
    if past:
        st.caption(f"{len(past)} reviews")
        for r in past[:8]:
            if st.button(f"📄 {r.stem[:28]}", key=f"h_{r.name}", use_container_width=True):
                st.session_state.selected_review = r
                st.rerun()
    else:
        st.caption("_No reviews yet_")

    st.divider()
    st.header("📚 Knowledge Base")
    kfiles = list_knowledge_files()
    for domain, files in kfiles.items():
        with st.expander(f"📁 {domain} ({len(files)})"):
            for f in files:
                st.caption(f"• {f}")

    st.divider()
    if groq_key:
        st.success(f"🔑 Groq ({groq_key[:6]}...)")
    else:
        st.error("No GROQ_API_KEY")

# ─── Show agent detail if clicked ─────────────────────────────
if st.session_state.selected_agent:
    key = st.session_state.selected_agent
    t = TEAM[key]
    if st.button("← Back to team"):
        st.session_state.selected_agent = None
        st.rerun()
    st.markdown(
        f"<div style='padding:24px;border-left:6px solid {t['color']};background:rgba(30,41,59,0.5);border-radius:8px;'>"
        f"<h1 style='margin:0;'>{t['emoji']} {t['name']}</h1>"
        f"<h3 style='color:{t['color']};margin-top:4px;'>{t['role']}</h3>"
        f"<p style='color:#cbd5e1;font-size:15px;line-height:1.6;'>{t['personality']}</p>"
        f"<hr style='border-color:#334155;'>"
        f"<p style='color:#94a3b8;font-size:13px;'><b>Catchphrase:</b> <i>\"{t['greeting']}\"</i></p>"
        f"<p style='color:#94a3b8;font-size:13px;'><b>Signs off as:</b> <code>{t['signature']}</code></p>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.stop()

# ─── Show past review if clicked ──────────────────────────────
if st.session_state.selected_review:
    st.subheader(f"📄 {st.session_state.selected_review.stem}")
    if st.button("← Back"):
        st.session_state.selected_review = None
        st.rerun()
    st.markdown(st.session_state.selected_review.read_text(encoding="utf-8"))
    st.stop()

# ─── Office World (always visible, top of page) ───────────────
st.subheader("🏢 The Office Floor")
world_slot = st.empty()
with world_slot.container():
    render_office_world(
        agent_statuses={k: "idle" for k in TEAM},
        height=380,
    )
st.caption("💡 Click an agent in the sidebar to see their profile")
st.divider()

# ─── Mode selector ────────────────────────────────────────────
st.subheader("🎯 Pick a review type")
mode = st.radio(
    "Mode",
    ["🔍 Full Review (all 5)", "🐛 Bugs (Priya + Jake)", "🔒 Security (Sam)", "💡 Explain (Luna)"],
    horizontal=True, label_visibility="collapsed",
)

mode_key = {
    "🔍 Full Review (all 5)": "full",
    "🐛 Bugs (Priya + Jake)": "bugs",
    "🔒 Security (Sam)":      "security",
    "💡 Explain (Luna)":      "explain",
}[mode]

st.divider()

# ─── Input ────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    st.subheader("📁 Upload code")
    uploaded = st.file_uploader("Upload", type=["py", "js", "ts", "jsx", "tsx", "go", "java", "rs", "cpp", "c", "cs", "rb", "php", "sql", "html", "css", "dart"], label_visibility="collapsed")
with col2:
    st.subheader("✍️ Or paste")
    pasted = st.text_area("Paste", height=160, placeholder="def hello():\n    print('world')", label_visibility="collapsed")

code = None; filename = "snippet.py"; language = "py"
if uploaded:
    code = uploaded.read().decode("utf-8", errors="replace")
    filename = uploaded.name
    language = Path(filename).suffix.lstrip(".") or "py"
elif pasted.strip():
    code = pasted

if code:
    with st.expander(f"👀 {filename} ({len(code)} chars)"):
        st.code(code[:2000] + ("\n...(truncated)" if len(code) > 2000 else ""), language=language)
    if len(code) > max_chars:
        st.warning(f"⚠️ Truncating {len(code)} → {max_chars} chars")
        code = code[:max_chars] + "\n# ...(truncated)"
    run = st.button(f"🚀 Have the team review it", type="primary", use_container_width=True)
else:
    st.info("👆 Upload or paste code to begin")
    run = False

# ─── RUN ──────────────────────────────────────────────────────
if run:
    if not groq_key:
        st.error("No GROQ_API_KEY"); st.stop()

    from crewai import Agent, Task, Crew, LLM

    llm = LLM(model=f"openai/{model_choice}", api_key=groq_key,
              base_url="https://api.groq.com/openai/v1", max_tokens=3000)

    # Who's in this run?
    agents_in_run = {
        "full":     ["alex", "priya", "jake", "sam", "luna"],
        "bugs":     ["priya", "jake"],
        "security": ["sam"],
        "explain":  ["luna"],
    }[mode_key]

    memory_block = ""
    if use_vault:
        memory_block = f"\n--- MEMORY ---\n{load_vault_knowledge()}\n--- END MEMORY ---\n"

    st.divider()

    # Reset session chat/timeline for this run
    st.session_state.chat_messages = []
    st.session_state.timeline_events = []

    # Live office floor at top (replace the static one above)
    world_slot_live = st.empty()
    speech_state = {}   # live speech bubbles

    def refresh_world(statuses, speaker=None, walking=None, bubbles=None):
        with world_slot_live.container():
            render_office_world(
                agent_statuses=statuses,
                current_speaker=speaker,
                walking_to=walking,
                speech_bubbles=bubbles or speech_state,
                height=420,
            )

    def set_bubble(agent_key, text):
        """Show a short speech bubble over an agent for the next render."""
        snippet = text[:80] + ("..." if len(text) > 80 else "")
        speech_state[agent_key] = snippet

    def clear_bubble(agent_key):
        speech_state.pop(agent_key, None)

    office_statuses = {k: "idle" for k in TEAM}
    for k in agents_in_run:
        office_statuses[k] = "waiting"
    refresh_world(office_statuses)

    progress = st.progress(0, text="Team gathering...")

    # Chat + timeline side-by-side
    chat_col, timeline_col = st.columns([3, 2])
    with chat_col:
        st.subheader("💬 #team-chat")
        chat_slot = st.empty()
        with chat_slot.container():
            render_chat([], height=320)
    with timeline_col:
        timeline_slot = st.empty()
        with timeline_slot.container():
            render_timeline([], height=320)

    def push_msg(agent_key, text):
        now = datetime.now().strftime("%H:%M:%S")
        st.session_state.chat_messages.append({
            "agent": agent_key, "text": text, "time": now,
        })
        with chat_slot.container():
            render_chat(st.session_state.chat_messages, height=320)

    def push_event(agent_key, action, detail=""):
        now = datetime.now().strftime("%H:%M:%S")
        st.session_state.timeline_events.append({
            "agent": agent_key, "action": action, "time": now, "detail": detail,
        })
        with timeline_slot.container():
            render_timeline(st.session_state.timeline_events, height=320)

    def update_office(state):
        """Legacy — now routes to office world."""
        for k, v in state.items():
            office_statuses[k] = v.get("status", "idle")
        refresh_world(office_statuses)

    # ─── Greetings — each agent "arrives" at their desk ───────
    for agent_key in agents_in_run:
        office_statuses[agent_key] = "talking"
        set_bubble(agent_key, TEAM[agent_key]["greeting"])
        refresh_world(office_statuses, speaker=agent_key)
        push_msg(agent_key, TEAM[agent_key]["greeting"])
        push_event(agent_key, "Arrived at the office", f"Role: {TEAM[agent_key]['role']}")
        time.sleep(0.5)
        clear_bubble(agent_key)
        office_statuses[agent_key] = "waiting"
    refresh_world(office_statuses)

    # ─── Build agents with personalities + domain knowledge ───
    def mk_agent(key, goal):
        knowledge = load_knowledge_for(key, max_chars=6000)
        return Agent(
            role=f"{TEAM[key]['role']} named {TEAM[key]['name']}",
            goal=goal,
            backstory=get_personality_prompt(key) + knowledge + memory_block,
            llm=llm, verbose=False, allow_delegation=False,
        )

    priya = mk_agent("priya", "Review the code for bugs, bad patterns, logic errors. Catch things juniors miss.")
    jake  = mk_agent("jake",  "Ask 'why does this work?' Add fresh-eyes observations. Flag anything confusing.")
    sam   = mk_agent("sam",   "Find security vulnerabilities. Severity rank. OWASP references. Attacker mindset.")
    luna  = mk_agent("luna",  "Explain findings in human English. Note where docs are missing.")
    alex  = mk_agent("alex",  "Make the final merge/block call. Combine team findings into one clean verdict.")

    agents_map = {"alex": alex, "priya": priya, "jake": jake, "sam": sam, "luna": luna}

    code_block = f"```{language}\n{code}\n```"
    tasks = []

    if mode_key == "full":
        t_priya = Task(
            description=f"Review this code for bugs/quality:\n{code_block}\nBullet points. Short. In your voice.",
            expected_output="Bug and quality findings in Priya's voice.",
            agent=priya, context=[],
        )
        t_jake = Task(
            description=f"Give FRESH-EYES observations on this code:\n{code_block}\nFlag confusing parts, ask 'why?' Short.",
            expected_output="Junior-dev perspective notes.",
            agent=jake, context=[t_priya],
        )
        t_sam = Task(
            description=f"SECURITY audit of this code:\n{code_block}\nSeverity + OWASP + attack scenario. In your voice.",
            expected_output="Security vulnerabilities.",
            agent=sam, context=[t_priya],
        )
        t_luna = Task(
            description=f"Note where DOCUMENTATION is missing/unclear:\n{code_block}\nShort list.",
            expected_output="Documentation gaps.",
            agent=luna, context=[t_priya],
        )
        t_alex = Task(
            description=(
                f"Combine the team's findings on `{filename}` into ONE PR comment:\n\n"
                "# Code Review — {filename}\n\n"
                "## 🚨 Blockers\n## ⚠️ Should Fix\n## 💡 Nice to Have\n## ✅ Good\n## Verdict\n"
                "APPROVE | REQUEST CHANGES | BLOCK — 1 sentence why.\n\n"
                "Under 300 words. Sign as Alex."
            ),
            expected_output="Final PR comment.",
            agent=alex, context=[t_priya, t_jake, t_sam, t_luna],
        )
        tasks = [t_priya, t_jake, t_sam, t_luna, t_alex]

    elif mode_key == "bugs":
        t_priya = Task(
            description=f"Review bugs in this code:\n{code_block}\nBullet points.",
            expected_output="Bug list.", agent=priya, context=[],
        )
        t_jake = Task(
            description=f"Fresh eyes on same code:\n{code_block}\nWhat seems weird?",
            expected_output="Confusion list.", agent=jake, context=[t_priya],
        )
        tasks = [t_priya, t_jake]

    elif mode_key == "security":
        t_sam = Task(
            description=f"Security audit:\n{code_block}\nSeverity + OWASP + attack.",
            expected_output="Severity-sorted vulnerabilities.", agent=sam, context=[],
        )
        tasks = [t_sam]

    elif mode_key == "explain":
        t_luna = Task(
            description=f"Explain this code in plain English:\n{code_block}\nShort, warm, section by section.",
            expected_output="Plain-English walkthrough.", agent=luna, context=[],
        )
        tasks = [t_luna]

    # Map tasks -> agent key for live tracking
    task_to_agent_key = {}
    for t in tasks:
        for k, ag in agents_map.items():
            if t.agent is ag:
                task_to_agent_key[id(t)] = k
                break

    try:
        progress.progress(10, text="Team starting...")
        start = time.time()

        # ─── LIVE ORCHESTRATION — run tasks one at a time ─────
        task_outputs = {}      # id(task) -> output text
        final_md = ""
        total_tasks = len(tasks)

        for idx, task in enumerate(tasks):
            agent_key = task_to_agent_key.get(id(task), "alex")
            agent_meta = TEAM[agent_key]

            # Set this agent to WORKING, others to waiting
            for k in agents_in_run:
                office_statuses[k] = "done" if k in [task_to_agent_key.get(id(t)) for t in tasks[:idx]] else ("working" if k == agent_key else "waiting")

            # Show "thinking" bubble while they work
            set_bubble(agent_key, "💭 Thinking...")
            refresh_world(office_statuses, speaker=agent_key)
            push_event(agent_key, "Started task", f"{idx+1}/{total_tasks}")
            push_msg(agent_key, f"⏳ _thinking about this..._")

            pct = int(10 + (80 * idx / total_tasks))
            progress.progress(pct, text=f"🏃 {agent_meta['name']} is working... ({idx+1}/{total_tasks})")

            # Build context string from previously-finished tasks it depends on
            context_text = ""
            if task.context:
                for ctx_task in task.context:
                    prev_output = task_outputs.get(id(ctx_task), "")
                    if prev_output:
                        prev_agent_key = task_to_agent_key.get(id(ctx_task), "team")
                        prev_name = TEAM.get(prev_agent_key, {}).get("name", "Team")
                        context_text += f"\n\n--- {prev_name}'s findings ---\n{prev_output}"

            # Inject context into task description temporarily
            original_desc = task.description
            if context_text:
                task.description = original_desc + "\n\nTEAM CONTEXT (what others said):" + context_text

            # Actually run this agent's task
            task_start = time.time()
            # Ensure context is a list (not CrewAI's _NotSpecified sentinel)
            if not isinstance(task.context, list):
                task.context = []
            try:
                output = task.execute_sync()
                output_text = str(output.raw if hasattr(output, "raw") else output)
            except Exception as task_err:
                output_text = f"[Error: {task_err}]"
            finally:
                task.description = original_desc  # restore

            task_duration = time.time() - task_start
            task_outputs[id(task)] = output_text

            # Update chat with the REAL output
            if st.session_state.chat_messages and st.session_state.chat_messages[-1]["text"].startswith("⏳"):
                st.session_state.chat_messages.pop()

            preview = output_text[:400] + ("..." if len(output_text) > 400 else "")
            push_msg(agent_key, preview)
            push_event(agent_key, f"Finished in {task_duration:.1f}s", f"Produced {len(output_text)} chars")

            # Short bubble preview with ACTUAL output
            short_bubble = output_text.split("\n")[0][:70] + "..."
            set_bubble(agent_key, short_bubble)

            # Walk to Alex (if not Alex) to deliver the report
            if agent_key != "alex" and "alex" in TEAM:
                office_statuses[agent_key] = "walking"
                refresh_world(office_statuses, walking={agent_key: "alex"})
                time.sleep(0.6)  # time to see the walk

            # Mark done, back to desk, bubble clears
            office_statuses[agent_key] = "done"
            clear_bubble(agent_key)
            refresh_world(office_statuses)

            # Keep the last task's output as the final markdown
            final_md = output_text

        total = time.time() - start
        progress.progress(100, text=f"✅ Team done in {total:.1f}s")

        st.divider()
        st.subheader(f"📋 Final Report — {filename}")
        st.markdown(final_md)

        saved = save_review(filename, final_md, mode_key)
        st.success(f"🧠 Saved: `{saved.relative_to(Path(__file__).parent)}`")

        st.download_button("💾 Download report", data=final_md,
                           file_name=f"{mode_key}_{filename}.md",
                           mime="text/markdown", use_container_width=True)

    except Exception as e:
        for k in agents_in_run:
            office_statuses[k] = "idle"
        refresh_world(office_statuses)
        push_msg("alex", f"Something broke, boss. Error: `{e}`")
        push_event("alex", "Error occurred", str(e)[:100])
        progress.progress(0, text="Error")
        with st.expander("🐛 Full error"):
            import traceback
            st.code(traceback.format_exc())
