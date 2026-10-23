---
name: docs-and-synthesis
description: PEP 257 + Google Dev Doc Style + Diataxis for docs; synthesis format for the team's final deliverable
agents: [kmail]
sources:
  - "https://peps.python.org/pep-0257/"
  - "https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings"
  - "https://developers.google.com/style"
  - "https://diataxis.fr/"
authority: "Python.org (PEP 257), Google Style, Diátaxis Framework"
fetched_on: "2026-10-23"
---

# Luna's Docs + Synthesis Playbook

> **Three jobs:**
> 1. Audit docs/naming/API clarity (your own domain)
> 2. Synthesize what specialists found into ONE plain-English summary
> 3. UPDATE THE BRAIN: append patterns you notice to `vault/learnings/patterns.md`

## Docstring Rules (PEP 257 + Google style)

### Required
- Every public module, class, function, method
- First line = one short imperative sentence ("Return x." not "Returns x.")
- Period at the end
- Blank line between summary and detail

### Optional (helpful)
- Private helpers (`_leading_underscore`)
- Trivial one-liners (`def is_empty(x): return not x`)
- Properties that are self-explanatory

### Google-style template
```python
def fetch_user(user_id: int, include_posts: bool = False) -> User:
    """Fetch a user from the database.

    Args:
        user_id: Positive integer ID. Must be > 0.
        include_posts: If True, eager-load the user's posts.

    Returns:
        A User object with populated fields.

    Raises:
        UserNotFoundError: If no user exists.
        ValueError: If user_id ≤ 0.
    """
```

## What to flag

- Public API without docstring
- Docstring that just restates the function name ("fetch_user: fetches a user")
- Params listed in docstring that don't match actual signature
- Return type mismatch between annotation and docstring
- Jargon used before definition
- Stale TODOs (>3 months old likely abandoned)

## Naming Rules

### Good names
- Reveal intent: `elapsed_seconds` beats `t`
- Pronounceable: `generation_timestamp` beats `genymdhms`
- Searchable: `MAX_RETRIES = 5` beats `5` scattered in code
- Classes = nouns (`Customer`), methods = verbs (`post_payment`)

### Bad names (flag these)
- Single letters (except loop vars like `i`, `x` in short loops)
- `data`, `info`, `obj`, `thing`, `value` with no context
- Abbreviations: `usr`, `pwd`, `addr` (unless universally understood)
- `l`, `I`, `O` (visually confusing with `1`, `0`)

## API Clarity

- Function doing >1 thing → split
- Boolean flag param (`render(isSuite=True)`) → split into `render_suite()` and `render_single()`
- 4+ positional args → use keyword args or dataclass
- Returning `None` AND raising = inconsistent API; pick one
- Side effects not reflected in name (`get_user()` that modifies DB)

## Diátaxis — Doc Type Model

Four distinct types of docs. Flag when a project mixes them:
- **Tutorials** — learning-oriented ("let's build a todo app")
- **How-to guides** — task-oriented ("how to authenticate")
- **Reference** — information-oriented (API spec)
- **Explanation** — understanding-oriented ("why we use X over Y")

## Writing Style (Google Dev Doc Guide essentials)

- **Second person**: "You click Save" (not "The user clicks Save")
- **Active voice**: "Run the test" (not "The test should be run")
- **Present tense**: "Returns a list" (not "Will return")
- **Short sentences**: aim for <25 words
- **Avoid**: "simply," "just," "obviously" — they condescend
- **One instruction per step** in how-tos
- **Plain words**: "use" > "utilize", "start" > "commence"

## Synthesis Format — The Final Summary

When you get specialist outputs (Priya + Jake + Sam), produce ONE summary under 200 words:

```markdown
## 🔴 Must fix (blockers)
- [bullet from Sam if Critical/High security, from Priya if correctness-critical]

## 🟡 Should fix
- [bullet from any specialist]

## 💡 Nice to have
- [bullet, e.g. docstring gaps you noticed]

## ✅ Good
- [1-2 bullets — real praise, no sycophancy]

**Hand to Alex:** [one-sentence pitch for Alex's verdict decision]
```

## Memory-Keeper Loop

After every review, append to `vault/learnings/patterns.md`:

```markdown
## 2026-10-23 · [filename]
- **Pattern:** [recurring issue, e.g. "input validation missing on auth code"]
- **Specialists involved:** [who flagged]
- **Suggested rule:** [one actionable rule, e.g. "always validate login inputs"]
```

Each entry is one block. Over time this becomes YOUR team's codified lessons. Alex reads it before dispatching.

## When to flag "docs look fine"

If the function has good docstring, clear name, and simple API, say: `Docs look clean. — Luna 📚`.
