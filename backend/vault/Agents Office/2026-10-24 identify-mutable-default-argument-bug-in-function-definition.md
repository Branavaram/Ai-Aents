---
agent: PRIYA
department: CODE REVIEW
task: mvlz7gs2767o
done: 2026-10-24T05:46:28.113Z
skills: client-reply, house-style, python-correctness
model: GPT-OSS 120B (Groq)
---
# Identify mutable default argument bug in function definition

🐛 example.py:1 · mutable default argument `x=[]` shares the same list across calls · leads to unexpected state retention and hard‑to‑track bugs (e.g., items added in one call appear in later calls) · 💡 change signature to `def f(x=None):` and inside do `if x is None: x = []` 

— Priya 👩‍💻  
Skill: python-correctness

---
Read: [[2026-10-23 identify-and-address-security-flaws-in-login-and-profile-loa]] · [[2026-10-24 identify-security-vulnerabilities-in-login-and-pickle-usage]] · [[2026-10-24 identify-security-vulnerabilities-in-login-and-profile-loadi]] · [[coding_style]]
