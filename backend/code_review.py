import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─── Setup Groq via OpenAI-compatible endpoint ────────────────
groq_key = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_KEY"] = groq_key
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"

from crewai import Agent, Task, Crew, LLM

# ─── Read the code to review ──────────────────────────────────
# Usage:  python code_review.py path/to/your/file.py
# If no path given, default to "my_code.py" in current folder
if len(sys.argv) > 1:
    code_path = Path(sys.argv[1])
else:
    code_path = Path("my_code.py")

if not code_path.exists():
    print(f"ERROR: Path not found: {code_path}")
    print("Usage: python code_review.py <path-to-your-file>")
    sys.exit(1)

if code_path.is_dir():
    print(f"\n'{code_path}' is a FOLDER, not a file.")
    print("\nCode files found inside (pick one):\n")
    code_exts = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".java",
                 ".rs", ".cpp", ".c", ".cs", ".rb", ".php", ".sql", ".html", ".css"}
    files = sorted(f for f in code_path.rglob("*") if f.is_file() and f.suffix.lower() in code_exts)
    if not files:
        print("  (no code files found)")
    else:
        for f in files[:30]:
            print(f"  {f}")
        if len(files) > 30:
            print(f"  ... and {len(files)-30} more")
    print(f'\nNow run:  python code_review.py "<path-to-one-file-above>"')
    sys.exit(0)

code_to_review = code_path.read_text(encoding="utf-8", errors="replace")

# Safety: if file is huge, truncate to avoid blowing past model limits
MAX_CHARS = 8000
if len(code_to_review) > MAX_CHARS:
    print(f"⚠️  File is {len(code_to_review)} chars — truncating to first {MAX_CHARS} for review")
    code_to_review = code_to_review[:MAX_CHARS] + "\n\n# ...(file truncated for review)..."
language = code_path.suffix.lstrip(".") or "text"  # py, js, ts, etc.

print(f"\nReviewing: {code_path}  ({len(code_to_review)} chars, {language})")

# ─── The LLM (brain) ──────────────────────────────────────────
llm = LLM(
    model="openai/openai/gpt-oss-120b",
    api_key=groq_key,
    base_url="https://api.groq.com/openai/v1",
    max_tokens=4000,
)

# ─── AGENT 1: The Code Reviewer ───────────────────────────────
reviewer = Agent(
    role="Senior Software Engineer and Code Reviewer",
    goal=(
        "Review code for bugs, unclear logic, bad patterns, and "
        "code smells. Give specific, actionable feedback."
    ),
    backstory=(
        "You've been writing code for 15 years. You've seen every bug, "
        "every anti-pattern, every 'this will work in production' lie. "
        "You care about quality but you're not a jerk about it. "
        "You explain WHY something is wrong, not just that it is."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# ─── AGENT 2: The Security Specialist ─────────────────────────
security = Agent(
    role="Application Security Engineer",
    goal=(
        "Find security vulnerabilities the general reviewer missed: "
        "injection attacks, auth issues, secret leaks, insecure crypto, "
        "unsafe deserialization, path traversal, DoS vectors."
    ),
    backstory=(
        "You're an ex-pentester turned AppSec engineer. You find "
        "vulnerabilities in production code every week. You think "
        "like an attacker: 'How would I break this?' You rank issues "
        "by severity (Critical / High / Medium / Low) and reference "
        "OWASP categories when you can."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# ─── AGENT 3: The Summarizer ──────────────────────────────────
summarizer = Agent(
    role="Engineering Lead writing the final PR comment",
    goal=(
        "Combine the Reviewer and Security reports into one clean, "
        "scannable PR comment that a developer can read in 60 seconds "
        "and act on immediately."
    ),
    backstory=(
        "You're the engineering lead who reviews PRs after the specialists. "
        "You hate walls of text. You rank issues by what blocks a merge. "
        "You write like a human, not a corporate robot. You end every "
        "review with a clear verdict: APPROVE, REQUEST CHANGES, or BLOCK."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# ─── TASK 1: General review ───────────────────────────────────
review_task = Task(
    description=(
        f"Review this {language} code (from file: {code_path.name}) "
        f"for bugs, code quality, and bad patterns:\n\n"
        f"```{language}\n{code_to_review}\n```\n\n"
        "For each issue, state function/line area, problem, why, and fix. "
        "Keep it concise — bullet points, not essays."
    ),
    expected_output="A concise list of code quality issues.",
    agent=reviewer,
)

# ─── TASK 2: Security review ──────────────────────────────────
security_task = Task(
    description=(
        f"Review this {language} code for SECURITY vulnerabilities:\n\n"
        f"```{language}\n{code_to_review}\n```\n\n"
        "Build on the general reviewer's findings. For each issue list: "
        "severity (Critical/High/Medium/Low), function/line area, OWASP "
        "category, one-line attack scenario, and one-line fix."
    ),
    expected_output="A severity-sorted list of security vulnerabilities.",
    agent=security,
    context=[review_task],
)

# ─── TASK 3: Summarize into PR comment ────────────────────────
summary_task = Task(
    description=(
        f"Combine the Reviewer and Security findings for `{code_path.name}` "
        "into a clean PR comment. Format in markdown:\n\n"
        f"# Code Review — {code_path.name}\n\n"
        "## 🚨 Blockers (must fix before merge)\n"
        "- bullet points, one line each\n\n"
        "## ⚠️ Should Fix\n"
        "- bullet points, one line each\n\n"
        "## 💡 Nice to Have\n"
        "- bullet points, one line each\n\n"
        "## ✅ Good Practices Noticed\n"
        "- bullet points\n\n"
        "## Verdict\n"
        "APPROVE | REQUEST CHANGES | BLOCK — with 1 sentence why.\n\n"
        "Keep the WHOLE output under 300 words. No code blocks. "
        "Dev should scan it in 60 seconds."
    ),
    expected_output="A clean markdown PR comment under 300 words.",
    agent=summarizer,
    context=[review_task, security_task],
    output_file="review_report.md",
)

# ─── CREW ─────────────────────────────────────────────────────
crew = Crew(
    agents=[reviewer, security, summarizer],
    tasks=[review_task, security_task, summary_task],
    verbose=True,
)

# ─── RUN ──────────────────────────────────────────────────────
print("\n" + "="*60)
print(f"🔍 CODE REVIEW CREW — Reviewing {code_path.name}")
print("="*60 + "\n")

result = crew.kickoff()

print("\n" + "="*60)
print("📋 FINAL PR COMMENT:")
print("="*60)
print(result)
print(f"\n💾 Saved to: review_report.md")
