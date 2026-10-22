# Security Patterns Reference

> Common security patterns the Security agent should check for.
> Add new patterns here as you learn them.

## Critical Patterns (always flag)
- **Hardcoded credentials**: passwords, API keys, tokens in source code
- **SQL injection**: f-string or `%` formatting in SQL queries
- **Command injection**: `os.system()`, `subprocess` with `shell=True`
- **Insecure deserialization**: `pickle.load()`, `yaml.load()` (not `safe_load`)
- **Path traversal**: user input used in file paths without validation
- **Code execution**: `eval()`, `exec()` on user input
- **SSRF**: user-controlled URLs in `requests.get()`

## High Patterns
- **Weak crypto**: MD5, SHA1 for passwords (use bcrypt/argon2)
- **Plain-text passwords**: stored anywhere
- **Missing auth**: endpoints with no authentication check
- **CSRF**: state-changing requests without CSRF protection
- **Open redirects**: user-controlled redirect URLs
- **Insecure randomness**: `random` module for security (use `secrets`)

## Medium Patterns
- **Verbose errors**: stack traces leaked to end users
- **Missing rate limits**: on login, API, expensive endpoints
- **CORS misconfigured**: `*` with credentials
- **Missing HTTPS**: `http://` in production URLs
- **Session fixation**: not regenerating session ID on login

## OWASP Top 10 (2021) Reference
- A01: Broken Access Control
- A02: Cryptographic Failures
- A03: Injection
- A04: Insecure Design
- A05: Security Misconfiguration
- A06: Vulnerable Components
- A07: Authentication Failures
- A08: Software/Data Integrity Failures
- A09: Security Logging Failures
- A10: Server-Side Request Forgery (SSRF)
