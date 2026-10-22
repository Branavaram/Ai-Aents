# Python Anti-Patterns

> **Source:** [docs.quantifiedcode.com/python-anti-patterns](https://docs.quantifiedcode.com/python-anti-patterns/)
> **Use:** Specific Python mistakes to flag.

## Correctness Anti-Patterns

### Mutable default argument
```python
# BAD — list is shared across all calls!
def append_item(x, items=[]):
    items.append(x)
    return items

# GOOD
def append_item(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

### Modifying list while iterating
```python
# BAD — skips items
for item in my_list:
    if condition:
        my_list.remove(item)

# GOOD — use comprehension
my_list = [i for i in my_list if not condition(i)]
```

### Using `is` to compare values (not identity)
```python
if x is 5:        # BAD — works by accident for small ints
if x == 5:        # GOOD

if name is "":    # BAD
if name == "":    # GOOD (or `if not name:`)

if x is None:     # GOOD — None is a singleton
```

### Bare except
```python
# BAD — catches EVERYTHING including KeyboardInterrupt, SystemExit
try:
    risky()
except:
    pass

# GOOD — be specific
try:
    risky()
except ValueError as e:
    logger.warning(f"Expected error: {e}")
```

### Not using context managers
```python
# BAD — file not closed if exception
f = open("file.txt")
data = f.read()
f.close()

# GOOD
with open("file.txt") as f:
    data = f.read()
```

### String concatenation in a loop
```python
# BAD — creates new string each iteration
result = ""
for word in words:
    result += word

# GOOD
result = "".join(words)
```

## Maintainability Anti-Patterns

### Comparing types with `type()`
```python
# BAD — breaks inheritance
if type(x) == list:

# GOOD
if isinstance(x, list):
```

### Not using `enumerate`
```python
# BAD
i = 0
for item in items:
    print(i, item)
    i += 1

# GOOD
for i, item in enumerate(items):
    print(i, item)
```

### Using `range(len(x))` to iterate
```python
# BAD
for i in range(len(items)):
    print(items[i])

# GOOD
for item in items:
    print(item)
```

### Not using `zip` for parallel iteration
```python
# BAD
for i in range(len(names)):
    print(names[i], ages[i])

# GOOD
for name, age in zip(names, ages):
    print(name, age)
```

### Explicit `len()` for emptiness check
```python
if len(items) == 0:   # BAD
if not items:         # GOOD
```

### Returning more than one type
```python
# BAD — caller must check type
def find(x):
    if found:
        return value   # returns value
    else:
        return False   # returns bool!

# GOOD — consistent or raise
def find(x):
    if found:
        return value
    return None  # or raise NotFound
```

## Readability Anti-Patterns

### Lambda for simple name
```python
# BAD
sort_key = lambda x: x.name

# GOOD
def sort_key(x): return x.name
# OR use operator.attrgetter("name")
```

### Deeply nested conditionals
```python
# BAD
if a:
    if b:
        if c:
            if d:
                do_thing()

# GOOD — early return / guard clauses
if not a: return
if not b: return
if not c: return
if not d: return
do_thing()
```

### Using `global`
Almost always a sign of poor design. Pass values explicitly or use a class.

### "Magic numbers"
```python
# BAD
if score > 70:

# GOOD
PASSING_SCORE = 70
if score > PASSING_SCORE:
```

## Performance Anti-Patterns

### `list` when `set` would do (membership tests)
```python
# BAD — O(n) lookup
if item in big_list:

# GOOD — O(1) lookup
if item in big_set:
```

### Not using dict comprehensions
```python
# BAD
result = {}
for k, v in pairs:
    result[k] = v * 2

# GOOD
result = {k: v * 2 for k, v in pairs}
```

### Repeated expensive calls
```python
# BAD
for item in items:
    if expensive_check():
        ...

# GOOD
if expensive_check():
    for item in items:
        ...
```

---

## When reviewing Python, scan for:
1. Mutable default args
2. Bare `except:` catches
3. `type()` instead of `isinstance()`
4. String concatenation in loops
5. `range(len(x))` patterns
6. Deeply nested conditions
7. Magic numbers
8. `is` comparisons for non-None values
9. Missing context managers for files/connections
10. Inconsistent return types
