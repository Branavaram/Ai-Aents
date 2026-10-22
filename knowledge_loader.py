"""
Knowledge Loader — gives each agent only their domain-specific knowledge.
"""
from pathlib import Path

VAULT = Path(__file__).parent / "vault" / "knowledge"


# Which agent reads which knowledge folders
AGENT_DOMAINS = {
    "alex":    ["dev", "security", "writing"],  # engineering lead — reads all
    "priya":   ["dev"],                          # senior dev
    "jake":    ["junior", "dev"],                # junior dev — fresh eyes + general
    "sam":     ["security"],                     # security engineer
    "luna":    ["writing"],                      # technical writer
}


def load_knowledge_for(agent_key: str, max_chars: int = 8000) -> str:
    """Load all knowledge MDs for an agent's domains.

    Returns a formatted string ready to inject into the agent's backstory.
    """
    domains = AGENT_DOMAINS.get(agent_key, [])
    if not domains:
        return ""

    chunks = []
    for domain in domains:
        folder = VAULT / domain
        if not folder.exists():
            continue
        for md in sorted(folder.glob("*.md")):
            content = md.read_text(encoding="utf-8", errors="replace")
            chunks.append(f"\n\n═══ {domain.upper()} / {md.stem} ═══\n{content}")

    full = "".join(chunks).strip()
    if len(full) > max_chars:
        full = full[:max_chars] + "\n\n[... truncated for token budget ...]"

    if not full:
        return ""

    return (
        f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📚 YOUR DOMAIN KNOWLEDGE (industry standards)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{full}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"USE this knowledge when reviewing. Reference specific rules "
        f"(e.g. 'OWASP A03 Injection', 'PEP 8 naming', 'Bandit B602')."
    )


def list_knowledge_files():
    """Returns a dict of {domain: [filenames]} for sidebar display."""
    out = {}
    for domain_folder in VAULT.iterdir():
        if domain_folder.is_dir():
            out[domain_folder.name] = sorted(f.name for f in domain_folder.glob("*.md"))
    return out
