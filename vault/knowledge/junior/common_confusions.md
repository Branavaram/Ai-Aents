# Junior Developer Confusions

> **Use (Jake):** Code patterns that genuinely confuse new developers. If you see these in code, ask "wait, why does this work?" — the answer is often "it doesn't, actually."

## Python-specific "wait, what?" moments

### Mutable defaults
```python
def add(item, bag=[]):
    bag.append(item)
    return bag

add("x")  # ["x"]
add("y")  # ["x", "y"]  ← wait, what?
```
→ The default `[]` is shared across all calls. Juniors catch this because it feels wrong.

### Late binding closures
```python
funcs = [lambda: i for i in range(3)]
[f() for f in funcs]  # [2, 2, 2]  ← expected [0, 1, 2]
```
→ `i` is looked up when the lambda runs, not when defined.

### `is` vs `==`
```python
a = 256
b = 256
a is b  # True

a = 257
b = 257
a is b  # False  ← wait, what?
```
→ Python caches small ints. `is` tests identity, not value. Always use `==` for value comparison.

### Chained comparisons
```python
if 1 < x < 10:  # Pythonic
if 1 < x and x < 10:  # Verbose
```
Junior might not know the chain works. Confirm with them.

### String immutability + concatenation
```python
s = ""
for i in range(1000):
    s += str(i)  # O(n²) — slow!
```
→ Use `"".join(...)` or `list.append + join`.

### Walrus `:=` operator
```python
if (n := len(items)) > 10:
    print(f"Too many: {n}")
```
Junior might not know what `:=` does. Explain.

### Decorators
```python
@functools.cache
def expensive(x): ...
```
Hidden behavior. Ask: "do you know what @cache does?"

## General coding gotchas

### Off-by-one errors
```python
for i in range(len(items) - 1):  # misses last item? misses first?
```
Always double-check loop bounds.

### Integer division vs float
```python
5 / 2    # 2.5
5 // 2   # 2
5 % 2    # 1
```
In other languages (Java, C) `5/2 == 2`. Easy mistake.

### `and` / `or` return VALUES, not bools
```python
x = a or b  # x is a if truthy, else b (not necessarily True/False)
```

### `None` is NOT the same as `False` for everything
```python
if x:              # True for any truthy
if x is not None:  # Only False when x is literally None
```

### Modifying while iterating
```python
for item in my_list:
    if condition(item):
        my_list.remove(item)  # ← bugs, skips items
```

## Signs code was written by someone without experience

- Lots of nested `if/else` instead of early returns
- Variables named `data`, `info`, `value`, `obj` with no context
- Comments like `# increment i` (just restates code)
- Try/except around everything "just in case"
- Hardcoded constants scattered throughout
- Functions that do 5 unrelated things

## How to review as the "fresh eyes" person
1. **Read it once at normal speed.** What's confusing?
2. **Ask "why" questions.** "Why is this `is` not `==`?"
3. **Point out hidden complexity.** Decorators, context managers, metaclasses.
4. **Flag anything that would stump YOU** if you were new to this codebase.
5. **Praise clear code!** When code reads like English, say so.

## My reviewing voice (as Jake)
- Enthusiastic 🚀
- Honest about confusion ("I don't get this")
- Lots of emoji 😅 👀 💡
- End with questions, not demands
- Catch stuff that LOOKS normal but isn't
