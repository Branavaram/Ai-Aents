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
from team import TEAM, get_personality_prompt

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

# ─── Header ───────────────────────────────────────────────────
st.markdown("# 🏢 AI Dev Team Office")
st.caption("Watch 5 AI teammates review your code together — each with their own personality")
st.divider()

# ─── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.header("👥 Meet the Team")
    for key, t in TEAM.items():
        st.markdown(
            f"<div style='padding:8px;margin:4px 0;border-left:3px solid {t['color']};'>"
            f"<b>{t['emoji']} {t['name']}</b> <small style='color:#94a3b8;'>· {t['role']}</small>"
            f"</div>", unsafe_allow_html=True
        )

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
    if groq_key:
        st.success(f"🔑 Groq ({groq_key[:6]}...)")
    else:
        st.error("No GROQ_API_KEY")

# ─── Show past review if clicked ──────────────────────────────
if st.session_state.selected_review:
    st.subheader(f"📄 {st.session_state.selected_review.stem}")
    if st.button("← Back"):
        st.session_state.selected_review = None
        st.rerun()
    st.markdown(st.session_state.selected_review.read_text(encoding="utf-8"))
    st.stop()

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

    # Two-column layout: office left, chat right
    office_col, chat_col = st.columns([3, 2])

    with office_col:
        st.subheader("🏢 Office")
        office_slot = st.empty()
        office_state = {k: {"status": "waiting", "thought": ""} for k in agents_in_run}
        with office_slot.container():
            render_office(office_state, height=280)

        progress = st.progress(0, text="Team gathering...")

    with chat_col:
        st.subheader("💬 #team-chat")
        chat_slot = st.empty()
        st.session_state.chat_messages = []
        with chat_slot.container():
            render_chat([], height=320)

    def push_msg(agent_key, text):
        st.session_state.chat_messages.append({
            "agent": agent_key,
            "text": text,
            "time": datetime.now().strftime("%H:%M"),
        })
        with chat_slot.container():
            render_chat(st.session_state.chat_messages, height=320)

    def update_office(state):
        with office_slot.container():
            render_office(state, height=280)

    # ─── Greetings ────────────────────────────────────────────
    for agent_key in agents_in_run:
        push_msg(agent_key, TEAM[agent_key]["greeting"])
        office_state[agent_key] = {"status": "waiting", "thought": TEAM[agent_key]["greeting"][:40]}
        update_office(office_state)
        time.sleep(0.3)

    # ─── Build agents with personalities ──────────────────────
    def mk_agent(key, goal):
        return Agent(
            role=f"{TEAM[key]['role']} named {TEAM[key]['name']}",
            goal=goal,
            backstory=get_personality_prompt(key) + memory_block,
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
            agent=priya,
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
            expected_output="Bug list.", agent=priya,
        )
        t_jake = Task(
            description=f"Fresh eyes on same code:\n{code_block}\nWhat seems weird?",
            expected_output="Confusion list.", agent=jake, context=[t_priya],
        )
        tasks = [t_priya, t_jake]

    elif mode_key == "security":
        t_sam = Task(
            description=f"Security audit:\n{code_block}\nSeverity + OWASP + attack.",
            expected_output="Severity-sorted vulnerabilities.", agent=sam,
        )
        tasks = [t_sam]

    elif mode_key == "explain":
        t_luna = Task(
            description=f"Explain this code in plain English:\n{code_block}\nShort, warm, section by section.",
            expected_output="Plain-English walkthrough.", agent=luna,
        )
        tasks = [t_luna]

    used = [agents_map[k] for k in agents_in_run]
    crew = Crew(agents=used, tasks=tasks, verbose=False)

    try:
        # First agent starts working
        first = agents_in_run[0]
        office_state[first] = {"status": "working", "thought": "On it..."}
        update_office(office_state)
        push_msg(first, f"On it, let me dig in...")

        progress.progress(20, text="Team working...")
        start = time.time()

        with st.spinner(f"The team is reviewing `{filename}`..."):
            result = crew.kickoff()

        total = time.time() - start

        # Everyone done
        for k in agents_in_run:
            office_state[k] = {"status": "done", "thought": "Done ✅"}
        update_office(office_state)

        # Final message from last agent
        last = agents_in_run[-1]
        final_md = str(result)
        preview = final_md[:200] + "..." if len(final_md) > 200 else final_md
        push_msg(last, f"**Here's the final report:**\n\n{preview}")

        progress.progress(100, text=f"✅ Review done in {total:.1f}s")

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
            office_state[k] = {"status": "idle", "thought": "❌ error"}
        update_office(office_state)
        push_msg("alex", f"Something broke, boss. Error: `{e}`")
        progress.progress(0, text="Error")
        with st.expander("🐛 Full error"):
            import traceback
            st.code(traceback.format_exc())
