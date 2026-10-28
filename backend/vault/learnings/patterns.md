# Code Review Patterns Journal

> Luna appends one entry per team review. Over time this becomes your crew's codified lessons.

## 2026-10-24 · Review transferMoney function for bugs and security issues
- **Specialists:** PRIYA, SAM, JAKE
- **Luna's summary:**
  > ## 🔴 Must fix (blockers)
  > - Capitalized `Def` keyword → syntax error; the function never compiles.  
  > - `eval(f"process_{from_acc}()")` runs user‑controlled code, opening arbitrary code execution.  
  > - No authentication/authorization check; any caller can transfer from any account.
  > ## 🟡 Should fix
  > - Opening `transfers.log` without a context manager leaks file descriptors on error.  
  > - `amt` is not validated – negative or absurd values can corrupt balances.  
  > - Function always returns `True`, hiding failures from the caller.
- **Source task:** [[2026-10-24 review-transfermoney-function-for-bugs-and-security-issues]]

