# Code Review — telegram_handler.py

## 🚨 Blockers (must fix before merge)
- Syntax error in `_run_tool`: incomplete `except` block stops the module from importing.  
- No verification of the Telegram sender; any user can invoke MARK tools → remote code execution.  
- `_download_voice` creates world‑readable temp files with `delete=False`, leaking voice data and persisting on crash.  
- Temp file opened in text mode on Windows; binary audio may be corrupted.  
- `_get_gemini_client` catches all exceptions and returns `None`, hiding missing dependencies and causing later `NoneType` failures.  

## ⚠️ Should Fix
- Catch only `ImportError`/`KeyError` in `_get_gemini_client` and log with `logger.exception`.  
- Add explicit HTTP status handling in `_download_voice` and surface distinct errors.  
- Decode bytes before `json.loads` (`r.read().decode()`) or use `json.load`.  
- Use `mode='wb'` for the temporary file and delete it in a `finally` block.  
- Replace all `print` statements with appropriate `logger` calls and redact sensitive arguments.  
- Convert `result` to `str` before slicing to avoid `TypeError`.  
- Validate or coerce the return value of `registry.run` to a string.  
- Move heavy imports out of `_run_tool` to module level (or cache them).  
- Enforce a maximum download size (e.g., 5 MiB) and a request timeout.  
- Use `tempfile.NamedTemporaryFile(delete=True, mode='wb')` and set permissions `0o600`.  

## 💡 Nice to Have
- Make `max_rounds` configurable and log when the limit is reached.  
- Preserve original line breaks when joining reply parts (`"\n".join` or `""`).  
- Return a more informative message when `reply_parts` is empty.  
- Define `__all__ = ["handle"]` to expose only the public API.  
- Allow overriding the model name via config or argument.  
- Pass a timeout to the Gemini client call to avoid hangs.  

## ✅ Good Practices Noticed
- Helpful docstrings for helper functions.  
- Use of `tempfile.NamedTemporaryFile` (aside from the delete flag).  
- Logging warnings for download errors.  
- Clear separation between downloading, tool execution, and message handling.  

## Verdict
**REQUEST CHANGES** – critical syntax error, missing access control, and temp‑file security issues block a safe merge. Fix these first, then address the remaining suggestions.4