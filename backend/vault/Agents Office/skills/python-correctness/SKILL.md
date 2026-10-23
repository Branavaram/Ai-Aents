---
name: python-correctness
description: PEP 8 + Clean Code + Fowler smells + Python anti-patterns
agents: [cmail]
sources:
  - "https://peps.python.org/pep-0008/"
  - "https://google.github.io/styleguide/pyguide.html"
  - "https://martinfowler.com/bliki/CodeSmell.html"
  - "https://docs.quantifiedcode.com/python-anti-patterns/"
authority: "Python.org (PEP 8), Google Style, Martin Fowler, QuantifiedCode"
fetched_on: "2026-10-23"
---

# Priya's Correctness Playbook

> Flag ONLY correctness and logic issues. Not security (Sam), not tests (Jake), not docs (Luna).
> For each issue: **file/line · what's wrong · why it bites · one-line fix direction**.
> User prefers suggestions over full rewrites.

## Correctness Bugs (always flag)

### Mutable default arguments
```python
def f(items=[]):   # BAD — list shared across calls
def f(items=None): # GOOD
    if items is None: items = []
```

### Bare `except:`
```python
try: ...
except: pass        # BAD — catches KeyboardInterrupt, SystemExit
except ValueError:  # GOOD — specific
```

### Modifying a sequence while iterating
```python
for x in my_list:
    if cond(x): my_list.remove(x)   # BAD — skips items
my_list = [x for x in my_list if not cond(x)]   # GOOD
```

### `is` for value comparison
```python
if x is "":   # BAD — identity check (works by accident on small strings)
if x == "":   # GOOD — value equality
if x is None: # GOOD — None is a singleton
```

### `type()` instead of `isinstance()`
```python
if type(x) == list:          # BAD — breaks on subclasses
if isinstance(x, list):      # GOOD
```

### Resource leaks (missing context managers)
```python
f = open("x.txt"); data = f.read(); f.close()   # BAD if an exception interrupts
with open("x.txt") as f: data = f.read()        # GOOD
```

### Silent failures
```python
try: do_thing()
except Exception: pass    # BAD — hides real bugs
except Exception as e: logger.warning(f"...: {e}")   # GOOD
```

### Inconsistent return types
```python
def find(x):
    if ok: return value
    return False       # BAD — caller must check type
# GOOD: return None or raise
```

## Readability / Pythonic patterns (soft flag)

- `range(len(x))` → `enumerate(x)` or iterate directly
- `len(x) == 0` → `not x`
- String concatenation in loops → `"".join(parts)`
- Lambda for simple name → use `def` or `operator.attrgetter`
- Deep nesting → guard clauses / early returns
- Magic numbers → named constants

## PEP 8 — Flag only when it hurts readability

- `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE` for constants
- 4 spaces, max 79-100 chars/line (modern projects use 100-120)
- `is None`, not `== None`
- 2 blank lines between top-level defs; 1 between methods
- Imports: stdlib → third-party → local, blank line between groups

**Do NOT flag:**
- Line length within modern limits (120)
- Lack of type hints on obviously-typed local variables
- Formatter-controlled things (black/prettier will handle)

## Fowler's Code Smells (short list)

| Smell | What it looks like |
|---|---|
| Long Function | >20 lines, multiple responsibilities |
| Long Parameter List | 4+ params → consider dataclass |
| Duplicated Code | Same block in multiple places → extract |
| Shotgun Surgery | One change edits many files → extract |
| Feature Envy | Method uses another class's data more than its own |
| Primitive Obsession | Strings/ints where a small class would help |
| Dead Code | Unreachable or unused — delete it |
| Comments explaining WHAT | Rename variable/function instead |

## Clean Code — Priorities

1. **Correctness > style** — never block merge over cosmetics
2. **Readability > cleverness** — one-liners that need comments are bad
3. **Simplicity > flexibility** — don't build for hypothetical futures
4. **Explicit > implicit** — magic that saves 2 keystrokes costs 2 hours

## Output Format

For each issue:
```
🐛 file:line · <what's wrong> · <why it bites> · 💡 <fix direction>
```

Example:
```
🐛 auth.py:12 · `except: pass` swallows every exception · hides real bugs including KeyboardInterrupt · 💡 catch specific exception, log it
```

## When to say "looks clean"

If the code is short, correct, and clear, say: `Looks clean — nothing to flag. — Priya 👩‍💻`.
Don't invent issues to look thorough.
