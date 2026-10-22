# Pet Peeves — Don't Suggest These

> Things agents keep suggesting that I don't care about.
> Add to this list as the crew annoys you.

## Low-value suggestions to DEPRIORITIZE
- "Add type hints" — only mention if the function signature is confusing
- "Use pathlib instead of os.path" — only if actually broken
- "Add a docstring" — only for public API functions, not helpers
- "Variable name could be more descriptive" — only if truly unreadable
- "Consider using an f-string" — don't mention this, I know

## Things I don't need commentary on
- Line length (I run black/prettier)
- Trailing whitespace
- Import ordering (my IDE handles this)
- 2-space vs 4-space debates

## When to be SILENT (not every file needs feedback)
- If the code is less than 20 lines and clearly correct, say "Looks good."
- Don't invent issues to look thorough.
- Rank by severity — only mention Low issues after Critical/High are listed.

## Don't Write Code For Me
- I prefer SUGGESTIONS, not fixed code dumps.
- Say "consider doing X" instead of writing a 20-line rewrite.
- I want to learn by writing fixes myself.
- Code examples are fine, but keep them SHORT (3-5 lines).
