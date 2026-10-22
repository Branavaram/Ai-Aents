# PEP 8 — Python Style Guide (Essentials)

> **Source:** [python.org/dev/peps/pep-0008](https://peps.python.org/pep-0008/)
> **Use:** Industry-standard Python code style. Flag deviations when they genuinely harm readability.

## Naming Conventions
| Thing | Convention | Example |
|---|---|---|
| Function/variable | `snake_case` | `calculate_total()` |
| Class | `PascalCase` | `class UserAccount` |
| Constant | `UPPER_SNAKE` | `MAX_RETRIES = 5` |
| Private (convention) | `_leading_underscore` | `_internal_cache` |
| "Mangled" private | `__double_leading` | `__strict_private` |
| Module/package | `snake_case` | `data_loader.py` |
| Type variable | `PascalCase` | `UserId = NewType(...)` |

## Layout
- **4 spaces** per indent (never tabs)
- **Max line length:** 79 for code, 72 for docstrings/comments (many projects use 100-120)
- **Blank lines:** 2 between top-level defs, 1 between methods
- **Imports:**
  1. Standard library (`import os`)
  2. Third-party (`import requests`)
  3. Local (`from .utils import foo`)
  Separate groups with blank lines.

## Whitespace
```python
# Good
spam(ham[1], {eggs: 2})
if x == 4: pass
x = 1

# Bad
spam( ham[ 1 ], { eggs : 2 } )
if x==4:pass
x=1
```

## String Quotes
Pick single or double, be consistent. **Triple-double** for docstrings always.

## Comparisons
- `if x is None:` (not `if x == None:`)
- `if not x:` for empty check on sequences
- `if x is True:` only when actually comparing to the boolean (rare)

## Function/method design
- One function → one responsibility
- Max ~20 lines per function (soft rule)
- Max 3-4 arguments (use dataclass/dict for more)
- Return early (avoid deep nesting)

## Docstrings (PEP 257)
```python
def fetch_user(user_id: int) -> User:
    """Fetch a user by ID.

    Args:
        user_id: Positive integer ID.

    Returns:
        User object or None if not found.

    Raises:
        ValueError: If user_id is negative.
    """
```

## Modern Python (3.10+)
- Prefer `list[int]` over `List[int]`
- Use `|` instead of `Union` (`int | None` not `Optional[int]`)
- Use dataclasses or Pydantic for structured data
- Use `match` statements where they clarify
- Use `pathlib.Path` not `os.path.join`

---

## What to FLAG when reviewing:
- Variables named `l`, `I`, `O` (look like 1, 1, 0)
- Mixed tabs/spaces
- Function names in PascalCase or vice versa
- Overly long lines (>120 chars)
- Imports not grouped
- Missing docstrings on PUBLIC API (not every helper)
- Mutable default args: `def f(x=[])` → use `None`
- Bare `except:` catches EVERYTHING including KeyboardInterrupt
- Comparing to `None` with `==` instead of `is`

## What NOT to flag (common AI reviewer bloat):
- 2-space vs 4-space in formatter-controlled projects (black/prettier handles it)
- Line length within reasonable modern limits (120)
- Lack of type hints on obviously-typed local variables
- Underscore-prefixed private helpers without docstrings
