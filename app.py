"""
AI Code Review Crew — v3 with history, metrics, and focus modes
Run with:  streamlit run app.py
"""
import os
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# ─── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Code Review Crew",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Setup env ────────────────────────────────────────────────
load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_KEY"] = groq_key or ""
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"

VAULT = Path(__file__).parent / "vault"

# ─── Vault helpers ────────────────────────────────────────────
def load_vault_knowledge():
    knowledge = []
    for folder in ["profile", "knowledge", "projects"]:
        folder_path = VAULT / folder
        if folder_path.exists():
            for md_file in folder_path.glob("*.md"):
                content = md_file.read_text(encoding="utf-8", errors="replace")
                knowledge.append(f"### 📄 {folder}/{md_file.name}\n\n{content}\n")
    return "\n---\n".join(knowledge) if knowledge else "(vault is empty)"

def load_recent_reviews(limit=3):
    reviews_dir = VAULT / "reviews"
    if not reviews_dir.exists():
        return "(no past reviews yet)"
    reviews = sorted(reviews_dir.glob("*.md"), reverse=True)[:limit]
    if not reviews:
        return "(no past reviews yet)"
    chunks = []
    for r in reviews:
        chunks.append(f"### 📝 {r.name}\n\n{r.read_text(encoding='utf-8', errors='replace')[:1500]}")
    return "\n---\n".join(chunks)

def save_review(filename, review_markdown, mode):
    reviews_dir = VAULT / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d_%H%M")
    safe = filename.replace("/", "_").replace("\\", "_")
    out = reviews_dir / f"{date}_[{mode}]_{safe}.md"
    out.write_text(review_markdown, encoding="utf-8")
    return out

def list_past_reviews():
    """Returns list of past reviews, newest first."""
    reviews_dir = VAULT / "reviews"
    if not reviews_dir.exists():
        return []
    return sorted(reviews_dir.glob("*.md"), reverse=True)

# ─── Session state (for metrics) ──────────────────────────────
if "selected_review" not in st.session_state:
    st.session_state.selected_review = None
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0
if "total_reviews" not in st.session_state:
    st.session_state.total_reviews = 0

# ─── Header ───────────────────────────────────────────────────
st.markdown("# 🤖 AI Code Review Crew")
st.caption("3 specialist agents review your code — with shared memory 🧠")
st.divider()

# ─── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    model_choice = st.selectbox(
        "Model (via Groq)",
        ["openai/gpt-oss-120b", "openai/gpt-oss-20b"],
        index=0,
    )

    max_chars = st.slider("Max chars", 2000, 15000, 8000, 1000)

    use_vault = st.toggle("🧠 Use vault memory", value=True)

    st.divider()

    # ─── Review history panel ─────────────────────────────────
    st.header("📜 Review History")
    past_reviews = list_past_reviews()
    if not past_reviews:
        st.caption("_No reviews yet. Run one!_")
    else:
        st.caption(f"**{len(past_reviews)}** total — click any to open")
        for review in past_reviews[:10]:
            name = review.stem
            # Parse out mode and filename from stem
            # Format: 2026-10-22_1351_[full]_page.tsx
            parts = name.split("_", 2)
            if len(parts) >= 3 and "[" in parts[2]:
                date_part = parts[0]
                time_part = parts[1]
                rest = parts[2]
                mode_tag = rest.split("]")[0].strip("[")
                fname = rest.split("]_", 1)[1] if "]_" in rest else rest
                mode_emoji = {"full": "🔍", "bugs": "🐛", "security": "🔒", "explain": "💡"}.get(mode_tag, "📄")
                label = f"{mode_emoji} {fname[:20]} · {time_part}"
            else:
                label = f"📄 {name[:30]}"
            if st.button(label, key=f"rev_{review.name}", use_container_width=True):
                st.session_state.selected_review = review
                st.rerun()
        if len(past_reviews) > 10:
            st.caption(f"_...and {len(past_reviews) - 10} more_")

    st.divider()

    # ─── Vault stats ──────────────────────────────────────────
    st.header("🧠 Vault")
    vault_files = list(VAULT.rglob("*.md")) if VAULT.exists() else []
    reviews_count = len(past_reviews)
    col_a, col_b = st.columns(2)
    col_a.metric("Knowledge", len([f for f in vault_files if "reviews" not in str(f)]))
    col_b.metric("Reviews", reviews_count)

    st.divider()

    # ─── API status ───────────────────────────────────────────
    st.header("🔑 API")
    if groq_key:
        st.success(f"Groq ({groq_key[:6]}...)")
    else:
        st.error("No GROQ_API_KEY")

# ─── MAIN AREA ────────────────────────────────────────────────

# If user clicked a past review in sidebar, show it
if st.session_state.selected_review:
    st.subheader(f"📄 {st.session_state.selected_review.stem}")
    if st.button("← Back to new review"):
        st.session_state.selected_review = None
        st.rerun()
    st.markdown(st.session_state.selected_review.read_text(encoding="utf-8"))
    st.stop()

# ─── Review focus modes ───────────────────────────────────────
st.subheader("🎯 Review Mode")
mode = st.radio(
    "Mode",
    ["🔍 Full Review", "🐛 Bugs Only", "🔒 Security Only", "💡 Explain Code"],
    horizontal=True,
    label_visibility="collapsed",
)
mode_key = mode.split()[1].lower()  # "full", "bugs", "security", "explain"

mode_desc = {
    "full": "Full crew: Reviewer + Security + Summarizer",
    "bugs": "Just the Reviewer — fast bug check",
    "security": "Just the Security agent — vulnerability scan",
    "explain": "Simple English walkthrough of the code",
}
st.caption(f"ℹ️ {mode_desc[mode_key]}")

st.divider()

# ─── Input area ───────────────────────────────────────────────
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("📁 Upload file")
    uploaded_file = st.file_uploader(
        "Choose file",
        type=["py", "js", "ts", "jsx", "tsx", "go", "java", "rs", "cpp", "c", "cs", "rb", "php", "sql", "html", "css", "dart"],
        label_visibility="collapsed",
    )

with col2:
    st.subheader("✍️ Or paste code")
    pasted_code = st.text_area("Paste", height=180, placeholder="def hello():\n    print('world')", label_visibility="collapsed")

code_to_review = None
filename = "snippet.py"
language = "py"
if uploaded_file is not None:
    code_to_review = uploaded_file.read().decode("utf-8", errors="replace")
    filename = uploaded_file.name
    language = Path(filename).suffix.lstrip(".") or "py"
elif pasted_code.strip():
    code_to_review = pasted_code

if code_to_review:
    with st.expander(f"👀 Preview — {filename} ({len(code_to_review)} chars)"):
        st.code(code_to_review[:2000] + ("\n...(truncated)" if len(code_to_review) > 2000 else ""), language=language)

    if len(code_to_review) > max_chars:
        st.warning(f"⚠️ File is {len(code_to_review)} chars — reviewing first {max_chars}")
        code_to_review = code_to_review[:max_chars] + "\n\n# ...(truncated)"

    run_button = st.button(f"🚀 Run {mode}", type="primary", use_container_width=True)
else:
    st.info("👆 Upload a file or paste code above to begin")
    run_button = False

# ─── Run crew ─────────────────────────────────────────────────
if run_button:
    if not groq_key:
        st.error("❌ No GROQ_API_KEY")
        st.stop()

    from crewai import Agent, Task, Crew, LLM

    llm = LLM(
        model=f"openai/{model_choice}",
        api_key=groq_key,
        base_url="https://api.groq.com/openai/v1",
        max_tokens=4000,
    )

    # Memory block
    memory_block = ""
    if use_vault:
        memory_block = f"\n---\n🧠 **YOUR MEMORY**\n\n{load_vault_knowledge()}\n\nRecent reviews:\n{load_recent_reviews(2)}\n---\n"

    st.divider()
    st.subheader("👥 Crew in Action")

    # ─── Agent cards with avatars ─────────────────────────────
    AVATARS = {
        "reviewer": "🧑‍💻",
        "security": "🛡️",
        "summarizer": "📋",
        "explainer": "🎓",
    }

    # Decide which agents to show based on mode
    agents_in_this_run = {
        "full": ["reviewer", "security", "summarizer"],
        "bugs": ["reviewer"],
        "security": ["security"],
        "explain": ["explainer"],
    }[mode_key]

    cols = st.columns(len(agents_in_this_run))
    status_slots = {}
    for col, agent_name in zip(cols, agents_in_this_run):
        with col:
            status_slots[agent_name] = st.empty()
            status_slots[agent_name].info(f"# {AVATARS[agent_name]}\n**{agent_name.title()}**\n\n⏸️ Waiting")

    progress = st.progress(0, text="Starting the crew...")
    metrics_slot = st.empty()

    # ─── Define agents ────────────────────────────────────────
    reviewer = Agent(
        role="Senior Software Engineer and Code Reviewer",
        goal="Find bugs, bad patterns, code smells. Suggest, don't rewrite.",
        backstory=f"You've been writing code for 15 years. You suggest, you don't dump code. {memory_block}",
        llm=llm, verbose=False, allow_delegation=False,
    )
    security = Agent(
        role="Application Security Engineer",
        goal="Find security vulnerabilities, OWASP issues, injection, secrets.",
        backstory=f"Ex-pentester. Attacker mindset. Severity-ranked output. {memory_block}",
        llm=llm, verbose=False, allow_delegation=False,
    )
    summarizer = Agent(
        role="Engineering Lead writing the final PR comment",
        goal="Combine findings into a scannable PR comment.",
        backstory=f"You hate walls of text. End with APPROVE/REQUEST CHANGES/BLOCK. {memory_block}",
        llm=llm, verbose=False, allow_delegation=False,
    )
    explainer = Agent(
        role="Patient Senior Dev who explains code to junior devs",
        goal="Walk through the code in simple English, section by section.",
        backstory=f"You teach by explaining the WHY and the big picture, not just the what. {memory_block}",
        llm=llm, verbose=False, allow_delegation=False,
    )

    # ─── Build tasks per mode ─────────────────────────────────
    code_block = f"```{language}\n{code_to_review}\n```"
    tasks = []

    if mode_key == "full":
        t1 = Task(
            description=f"Review this {language} code ({filename}) for bugs and quality:\n\n{code_block}\n\nBullet points, respect user's style from memory.",
            expected_output="Prioritized list of code quality issues.",
            agent=reviewer,
        )
        t2 = Task(
            description=f"Security review of this {language} code:\n\n{code_block}\n\nBuild on reviewer. Severity, OWASP, attack scenario, suggested fix.",
            expected_output="Severity-sorted security vulnerabilities.",
            agent=security, context=[t1],
        )
        t3 = Task(
            description=f"Combine findings for `{filename}` into markdown PR comment:\n\n# Code Review — {filename}\n\n## 🚨 Blockers\n## ⚠️ Should Fix\n## 💡 Nice to Have\n## ✅ Good Practices\n## Verdict\nAPPROVE | REQUEST CHANGES | BLOCK — 1 sentence why.\n\nUnder 300 words. Suggest, don't dump code.",
            expected_output="Clean markdown PR comment under 300 words.",
            agent=summarizer, context=[t1, t2],
        )
        tasks = [t1, t2, t3]

    elif mode_key == "bugs":
        tasks = [Task(
            description=f"Find bugs and bad patterns in this {language} code ({filename}):\n\n{code_block}\n\nFor each issue: function/line, problem, why it's bad, suggested direction (no full rewrite). Keep it short.",
            expected_output="Clean bulleted bug report.",
            agent=reviewer,
        )]

    elif mode_key == "security":
        tasks = [Task(
            description=f"Security-only review of this {language} code ({filename}):\n\n{code_block}\n\nFor each vuln: severity, function, OWASP cat, attack scenario, suggested fix direction. Severity-sorted.",
            expected_output="Severity-sorted security vulnerabilities.",
            agent=security,
        )]

    elif mode_key == "explain":
        tasks = [Task(
            description=f"Explain this {language} code ({filename}) in simple English:\n\n{code_block}\n\nStructure: 1) What it does (big picture, 1-2 sentences). 2) Main parts (bullet each function/section with its purpose). 3) Any gotchas/complexities. Teach, don't just describe.",
            expected_output="Clear plain-English walkthrough.",
            agent=explainer,
        )]

    # Build crew with just the agents actually used
    agents_map = {"reviewer": reviewer, "security": security, "summarizer": summarizer, "explainer": explainer}
    used_agents = [agents_map[a] for a in agents_in_this_run]

    crew = Crew(agents=used_agents, tasks=tasks, verbose=False)

    # ─── Run with metrics ─────────────────────────────────────
    try:
        for agent_name in agents_in_this_run:
            status_slots[agent_name].warning(f"# {AVATARS[agent_name]}\n**{agent_name.title()}**\n\n🏃 Running...")
        progress.progress(10, text="Crew working...")
        start = time.time()

        with st.spinner(f"Running {mode}..."):
            result = crew.kickoff()

        total = time.time() - start

        for agent_name in agents_in_this_run:
            status_slots[agent_name].success(f"# {AVATARS[agent_name]}\n**{agent_name.title()}**\n\n✅ Done")

        progress.progress(100, text=f"✅ Done in {total:.1f}s")

        # Try to extract token usage
        token_info = ""
        try:
            usage = getattr(result, "token_usage", None)
            if usage:
                total_tokens = getattr(usage, "total_tokens", 0)
                st.session_state.total_tokens += total_tokens
                token_info = f" • {total_tokens:,} tokens"
        except Exception:
            pass

        st.session_state.total_reviews += 1

        # ─── Live metrics bar ─────────────────────────────────
        metrics_slot.success(
            f"⚡ **This run:** {total:.1f}s{token_info} • "
            f"**Session total:** {st.session_state.total_reviews} reviews, "
            f"{st.session_state.total_tokens:,} tokens • "
            f"**Cost:** $0.00 (Groq free tier) 🎉"
        )

        st.divider()
        st.subheader(f"📋 {mode} Result")
        final_md = str(result)
        st.markdown(final_md)

        # Save to vault
        saved = save_review(filename, final_md, mode_key)
        st.success(f"🧠 Saved to vault: `{saved.relative_to(Path(__file__).parent)}`")

        # Download
        st.download_button(
            "💾 Download as .md",
            data=final_md,
            file_name=f"{mode_key}_{filename}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    except Exception as e:
        for agent_name in agents_in_this_run:
            status_slots[agent_name].error(f"# {AVATARS[agent_name]}\n**{agent_name.title()}**\n\n❌ Failed")
        progress.progress(0, text="Error")
        st.error(f"Something broke: {e}")
        with st.expander("🐛 Full error"):
            import traceback
            st.code(traceback.format_exc())
