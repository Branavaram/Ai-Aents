# Bandit Security Rules (Python)

> **Source:** [bandit.readthedocs.io](https://bandit.readthedocs.io/en/latest/plugins/index.html)
> **Use:** Specific Python security anti-patterns Bandit detects. Reference these codes (B101-B700) when flagging.

## Assertions and asserts (B101)
- `assert` statements removed in optimized Python → don't rely on them for security

## Exec (B102)
- `exec(user_input)` → code execution. Never use.

## Shell injection (B602, B603, B604, B605, B606, B607)
- `subprocess.call("ls " + user)` with `shell=True` → command injection
- `os.system(cmd)` with user input → command injection
- `os.popen(cmd)` → same risk

## Hardcoded passwords (B105, B106, B107)
- String literals that look like passwords in default args, assignments

## SQL injection (B608)
- `cursor.execute("SELECT * FROM users WHERE id = %s" % user_id)` → string formatting in SQL
- `cursor.execute(f"...{user_id}...")` → f-string in SQL
- Fix: use `cursor.execute("... = ?", (user_id,))` parameterized queries

## Flask debug mode (B201)
- `app.run(debug=True)` → in production enables code execution via Werkzeug

## Insecure crypto (B303, B304, B305, B311, B321, B324)
- MD5/SHA1 for security → use SHA-256+
- `random.random()` for tokens → use `secrets.token_urlsafe()`
- DES, RC4 → broken, use AES-GCM
- FTP → use SFTP/HTTPS
- Telnet → use SSH

## Unsafe YAML/pickle (B301, B506, B403)
- `yaml.load()` → use `yaml.safe_load()`
- `pickle.loads(data)` on untrusted → RCE
- Importing `pickle` → audit all usage

## Request without timeout (B113)
- `requests.get(url)` with no timeout → hangs forever on slow endpoints

## Weak SSL/TLS (B502, B503, B504)
- `ssl.PROTOCOL_SSLv2/3`, `TLSv1`, `TLSv1_1` → deprecated
- `verify=False` on `requests` → MitM vulnerability

## XML External Entities (B313, B314, B405, B410)
- `xml.etree.ElementTree.parse(xml)` → XXE possible
- Use `defusedxml` library instead

## Try/except pass (B110)
- `except: pass` → silent failures hide security errors

## Hardcoded SQL password (B105 variants)
- Database URLs with passwords in source code

## eval / compile (B102, B103)
- `eval(user_input)` → code execution
- `compile(user_input, ...)` → risk if user controls input

## File permissions (B103)
- `os.chmod(f, 0o777)` → world-writable, bad

---

## When reviewing Python code, scan for:
1. Any `shell=True` in subprocess calls
2. Any `pickle.loads`, `yaml.load`, `eval`, `exec`
3. Any string formatting in SQL (`.format()`, `f""`, `%`)
4. Any hardcoded strings that look like keys/tokens/passwords
5. Any `verify=False` or `TLSv1`
6. Any `random.` used in security context
7. Any `assert` doing security checks

Flag each with the Bandit code (B###) + severity.
