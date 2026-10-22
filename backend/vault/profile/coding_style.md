# My Coding Style

> This note tells AI agents how I write code, so they review mine the way *I* would.
> Edit this freely — the more specific, the smarter the agents get.

## Languages I Code In
- Python (primary)
- JavaScript / TypeScript
- Dart / Flutter (mobile)

## Patterns I Prefer
- Type hints on all function parameters and returns
- `logger.info(...)` instead of `print(...)` in production code
- Context managers (`with open(...)`) for all file I/O
- Dataclasses or Pydantic over plain dicts
- `pathlib.Path` instead of `os.path.join`

## Patterns I Dislike
- `except Exception as e: pass` (silent failures)
- Mutable default arguments (`def f(x=[])`)
- Hardcoded secrets/credentials in code
- Giant 200+ line functions
- Comments that just restate the code

## Review Priorities (what matters most to me)
1. Security vulnerabilities (RCE, SQL injection, secrets leaked)
2. Correctness bugs (crashes, wrong outputs)
3. Error handling (what happens on failure?)
4. Readability (will future-me understand this?)
5. Performance (only if clearly bad)
6. Style (lowest priority — I use linters for this)

## My Experience Level
- Comfortable with: async/await, decorators, FastAPI, pytest
- Learning: AI agents (CrewAI, LangGraph), MCP, vector DBs
- Framework favorites: FastAPI, CrewAI, React, Flutter
