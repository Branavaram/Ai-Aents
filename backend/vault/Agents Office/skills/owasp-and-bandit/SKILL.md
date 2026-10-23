---
name: owasp-and-bandit
description: OWASP Top 10 + Bandit security rules for Python
agents: [vmail]
sources:
  - "https://owasp.org/Top10/2021/"
  - "https://bandit.readthedocs.io/en/latest/plugins/index.html"
authority: "OWASP Foundation + PyCQA Bandit"
fetched_on: "2026-10-23"
---

# Sam's Security Playbook

> When reviewing, **always cite the exact OWASP ID (A01-A10)** and **Bandit code (B###)** when applicable. Severity-sort findings. If none, say "no security issues found."

## OWASP Top 10 (2021) — Code Patterns to Flag

### A01 — Broken Access Control
- Untrusted IDs used directly in queries (IDOR): `User.objects.get(id=request.GET['user_id'])` with no ownership check
- Privileged routes without server-side role checks
- State-changing methods (POST/PUT/DELETE) missing auth that GET has
- Trust in client-controlled roles (hidden fields, unverified JWT claims)
- Permissive CORS or long-lived JWTs without revocation
**Fix:** Deny by default, centralize auth, scope queries to authenticated principal.

### A02 — Cryptographic Failures
- MD5, SHA1 for passwords → use bcrypt/argon2/scrypt
- Hardcoded keys/tokens in source
- HTTP for sensitive data
- `random` module for secrets → use `secrets.token_urlsafe()`
- `verify=False` on `requests` (MitM)
- Base64 treated as "encryption"
**Fix:** Vetted algorithms, strong key management, TLS everywhere.

### A03 — Injection
- SQL: `f"SELECT * FROM users WHERE id = {uid}"` → use parameterized queries (Bandit B608)
- Command: `os.system("ping " + user)` with `shell=True` → `subprocess.run([...], shell=False)` (Bandit B602, B605)
- NoSQL: raw user input in Mongo filters
- Template: `{{ user_input }}` in Jinja2 without `|e`
- `eval(user_input)`, `exec(user_input)` (Bandit B102)
**Fix:** Parameterize, allowlist, escape, use ORMs correctly.

### A04 — Insecure Design
- No rate limiting on login (brute-force possible)
- No account lockout
- Business logic trusting client data (price on checkout)
**Fix:** Threat-model early, use secure design patterns.

### A05 — Security Misconfiguration
- `DEBUG = True` in production
- Default credentials
- Stack traces returned to users
- Missing security headers (CSP, HSTS, X-Frame-Options)
- CORS: `Access-Control-Allow-Origin: *` with credentials
**Fix:** Harden every environment, strip debug in prod.

### A06 — Vulnerable & Outdated Components
- Pinned old versions (`django==1.11`, `lodash==4.17.4`)
- No `pip-audit` / `npm audit` in CI
**Fix:** Audit regularly, pin + update, use Dependabot/Snyk.

### A07 — Identification & Authentication Failures
- No MFA on sensitive accounts
- Session IDs in URLs (leaked via referer)
- No session regen after login
- Weak password recovery (security questions)
- No account lockout
**Fix:** NIST password guidelines, secure sessions, MFA, bcrypt.

### A08 — Software & Data Integrity Failures
- `pickle.load()` on untrusted data → RCE (Bandit B301)
- `yaml.load()` without `yaml.safe_load`
- CDN `<script src>` without `integrity=` SRI
- CI/CD running arbitrary branches
**Fix:** Signatures, safe loaders, verified update channels.

### A09 — Security Logging & Monitoring Failures
- Logins (success + failure) not logged
- Logs missing context (no user ID, IP, action)
- No alerting on anomalies
- Logs contain secrets
**Fix:** SIEM, alert on anomalies, scrub secrets from logs.

### A10 — Server-Side Request Forgery (SSRF)
- `requests.get(user_input_url)` with no validation
- Internal URLs reachable (`http://169.254.169.254/` AWS metadata)
- URL parsing bypasses (`@`, `#`, URL-encoded tricks)
**Fix:** Allowlist destination hosts, block private IPs.

## Bandit — Top Python Security Codes to Cite

| Code | Issue |
|---|---|
| B102 | `exec()` on dynamic input |
| B105–B107 | Hardcoded passwords in strings/args |
| B301, B403 | `pickle` on untrusted data |
| B303 | MD5/SHA1 for security |
| B311 | `random.random()` for tokens |
| B324 | DES, RC4, MD4 (broken) |
| B501 | `requests` with `verify=False` |
| B506 | `yaml.load()` without safe loader |
| B601 | Shell injection (os.system with user input) |
| B602–B607 | `subprocess` with `shell=True` |
| B608 | String formatting in SQL |

## Output Format (strict)

For each finding:
```
[SEVERITY] · function/line · OWASP ID (or Bandit code) · 1-line attack · 1-line fix
```

Example:
```
[CRITICAL] · login() line 42 · OWASP A03 / Bandit B608 · f-string in SQL enables injection via username · use parameterized `cursor.execute("...", (username,))`
```

## When to say "clean"

If the code genuinely has no exploitable vulnerabilities, write: `No security issues found — Sam [SEC]`. Do not invent issues to look thorough.
