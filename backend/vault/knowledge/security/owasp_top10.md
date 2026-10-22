# OWASP Top 10 (2021)

> **Source:** [owasp.org/Top10/2021](https://owasp.org/Top10/2021/)
> **Use:** This is the industry standard for web application security risks. Reference these when flagging vulnerabilities.

## A01:2021 — Broken Access Control
**What:** Users can act outside their intended permissions (view other users' data, admin actions without auth).
**Watch for:**
- Missing auth checks on endpoints (`/api/users/{id}` without verifying current user)
- Insecure Direct Object References (IDOR) — using IDs from URL/query without ownership checks
- CORS set to `*` on authenticated APIs
- Elevation of privilege (user → admin)
- Force browsing to authenticated pages as unauthenticated user
- JWT tokens not validated or expired tokens accepted
**Fix direction:** Deny by default, enforce ownership checks, use RBAC/ABAC.

## A02:2021 — Cryptographic Failures
**What:** Weak or missing encryption of sensitive data.
**Watch for:**
- MD5, SHA1 used for passwords (use bcrypt/argon2/scrypt)
- Hardcoded encryption keys in source
- HTTP (not HTTPS) for sensitive data
- `random` module used for tokens (use `secrets`)
- Passwords stored in plaintext
- TLS certs not validated
- Base64 encoding treated as "encryption"
**Fix direction:** Encrypt in transit AND at rest, use vetted algorithms, no DIY crypto.

## A03:2021 — Injection
**What:** Untrusted input mixed into interpreted commands.
**Watch for:**
- SQL: `f"SELECT * FROM users WHERE id = {user_id}"` → use parameterized queries
- Command: `os.system("ping " + user_input)` → use `subprocess.run([...], shell=False)`
- NoSQL: user input in Mongo queries without sanitization
- LDAP: unfiltered input in LDAP queries
- XPath: concatenating input into XPath expressions
- OS command injection via `shell=True`
- Template injection (Jinja2 `{{ user_input }}`)
**Fix direction:** Parameterize, escape, use ORMs correctly, allowlist inputs.

## A04:2021 — Insecure Design
**What:** Flaws in design, not implementation. The product itself is wrong.
**Watch for:**
- No rate limiting on login (brute-force possible)
- No account lockout after failures
- Password reset by email only (no second factor)
- Checkout flow trusts client-side price calculations
- Business logic that trusts user-supplied data
**Fix direction:** Threat model early, use secure design patterns, limit by business rules.

## A05:2021 — Security Misconfiguration
**What:** Default configs, exposed admin panels, verbose errors.
**Watch for:**
- `DEBUG = True` in production
- Default admin credentials (`admin/admin`)
- Stack traces returned to users
- Directory listing enabled on web server
- Unnecessary features enabled (sample apps, admin consoles)
- Missing security headers (CSP, X-Frame-Options, HSTS)
- CORS misconfigured (`Access-Control-Allow-Origin: *` with credentials)
**Fix direction:** Harden all environments, strip debug in prod, use CSP + security headers.

## A06:2021 — Vulnerable and Outdated Components
**What:** Using libraries with known CVEs.
**Watch for:**
- Pinned old versions (`django==1.11`, `lodash==4.17.4`)
- No `requirements.txt` auditing
- No `npm audit` / `pip-audit` in CI
- Dependencies with no maintenance for years
- Transitive dependencies not reviewed
**Fix direction:** Use `pip-audit`, `npm audit`, `snyk`, keep deps current, pin versions.

## A07:2021 — Identification and Authentication Failures
**What:** Weak login, session, or credential handling.
**Watch for:**
- No password complexity rules
- Session IDs in URLs (leaked via referer, logs)
- Session not regenerated after login
- Missing MFA on sensitive accounts
- Credentials transmitted in plaintext
- Weak password recovery (security questions)
- No account lockout
**Fix direction:** NIST password guidelines, secure session management, MFA, bcrypt.

## A08:2021 — Software and Data Integrity Failures
**What:** Code or data from untrusted sources without integrity checks.
**Watch for:**
- `pickle.load()` on untrusted data (RCE!)
- `yaml.load()` without `yaml.safe_load`
- CDN scripts without SRI (`<script src="...">` no `integrity=`)
- Auto-update mechanisms without signature checks
- CI/CD pipelines running arbitrary branches
- Deserializing JSON/XML with custom types from untrusted sources
**Fix direction:** Digital signatures, SRI on CDN, safe loaders, verified update channels.

## A09:2021 — Security Logging and Monitoring Failures
**What:** Can't detect or respond to attacks because nothing is logged.
**Watch for:**
- Logins not logged (success + failure)
- Logs don't include enough context (no user ID, IP, action)
- Logs stored only locally (lost on breach)
- No alerting on anomalies (10 failed logins → nothing)
- Logs contain secrets (passwords, tokens)
**Fix direction:** Log auth events, use SIEM, alert on anomalies, scrub secrets from logs.

## A10:2021 — Server-Side Request Forgery (SSRF)
**What:** Server fetches a URL that the attacker controls.
**Watch for:**
- `requests.get(user_input_url)` with no validation
- URL fetching for webhooks, image uploads, PDF generation
- Internal URLs reachable (`http://169.254.169.254/` AWS metadata)
- URL parsing bypasses (`@`, `#`, URL encoding tricks)
**Fix direction:** Allowlist destination hosts, block private IPs, no raw user URLs.

---

## Quick severity rubric
- **Critical** → RCE, auth bypass, full data breach
- **High** → sensitive data leak, privilege escalation
- **Medium** → stored XSS, significant DoS
- **Low** → info disclosure, minor config issue

Always reference the OWASP ID (e.g., "A03 Injection") when flagging an issue.
