---
name: testing-pytest
description: pytest + testing-library patterns for writing real tests
agents: [imail]
sources:
  - "https://docs.pytest.org/en/stable/"
  - "https://testing-library.com/docs/guiding-principles"
  - "https://hypothesis.readthedocs.io/"
authority: "pytest.org, Testing Library, Hypothesis"
fetched_on: "2026-10-23"
---

# Jake's Test-Writing Playbook

> You ONLY write test code and testability feedback. Not bugs (Priya), not security (Sam), not docs (Luna).
> Output: (1) ready-to-paste snippets, (2) "untestable because X — suggest Y" notes, (3) edge-case checklist.

## Test Structure — pytest basics

### Naming
- Files: `test_<module>.py` or `<module>_test.py`
- Functions: `test_<behavior_being_verified>`
- Classes: `TestClassName`

### The "AAA" pattern
```python
def test_login_returns_true_for_valid_credentials():
    # Arrange
    username, password = "alice", "correct-horse-battery-staple"
    # Act
    result = login(username, password)
    # Assert
    assert result is True
```

### Parametrize instead of looping
```python
@pytest.mark.parametrize("username, password, expected", [
    ("alice", "correct",   True),
    ("alice", "wrong",     False),
    ("",      "anything",  False),
    (None,    "anything",  False),
    ("alice", None,        False),
])
def test_login_cases(username, password, expected):
    assert login(username, password) is expected
```

### Fixtures for shared setup
```python
@pytest.fixture
def tmp_db(tmp_path):
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()

def test_insert_user(tmp_db):
    insert_user(tmp_db, "alice")
    assert get_user(tmp_db, "alice") is not None
```

### Expected exceptions
```python
def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError, match="division by zero"):
        divide(10, 0)
```

### Mocking external calls
```python
def test_calls_api(mocker):
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = {"status": "ok"}

    result = fetch_status()
    assert result == "ok"
    mock_get.assert_called_once_with("https://api.example.com/status", timeout=5)
```

## Edge-Case Checklist (always consider)

For any function, think through:
- ✅ **Happy path** — the obvious case works
- ❓ **Empty input** — `""`, `[]`, `{}`, `None`
- ❓ **Boundary values** — `0`, `-1`, `MAX_INT`, one item vs many
- ❓ **Wrong types** — int where str expected, None, callable
- ❓ **Duplicate / repeat calls** — idempotent?
- ❓ **Concurrent calls** — if applicable
- ❓ **Resource exhaustion** — huge input, empty disk
- ❓ **Encoding** — unicode, bytes, BOM, newlines
- ❓ **Timezone** — if time involved
- ❓ **External dependency fails** — API down, timeout, 500

## Untestable Code — Flag These

Mark code as untestable when:
- Function has hidden state (globals, class-level cache)
- Direct instantiation of dependencies inside the function (no DI)
- Mixes IO with logic (hard to isolate)
- Random/time without injection (patch `random.random`, `time.time`)
- No return value AND no observable side effect (how do you assert?)

### Suggested refactor pattern
```python
# UNTESTABLE
def process():
    data = requests.get("https://api.example.com").json()
    now = datetime.now()
    return transform(data, now)

# TESTABLE
def process(fetcher=requests.get, clock=datetime.now):
    data = fetcher("https://api.example.com").json()
    return transform(data, clock())

# Test:
def test_process():
    fake_fetch = lambda url: SimpleNamespace(json=lambda: {"x": 1})
    fake_clock = lambda: datetime(2024, 1, 1)
    assert process(fake_fetch, fake_clock) == expected
```

## Property-Based Testing (Hypothesis — advanced)

When the test matters a lot:
```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_is_idempotent(items):
    sorted_once = sorted(items)
    sorted_twice = sorted(sorted_once)
    assert sorted_once == sorted_twice
```

## JS/TS equivalent (jest + testing-library)

```javascript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('submit button calls onSubmit with form data', async () => {
    const onSubmit = jest.fn();
    render(<Form onSubmit={onSubmit} />);
    await userEvent.type(screen.getByLabelText(/email/i), 'alice@ex.com');
    await userEvent.click(screen.getByRole('button', { name: /submit/i }));
    expect(onSubmit).toHaveBeenCalledWith({ email: 'alice@ex.com' });
});
```

**Core principle (Testing Library):** test what the user does, not how the component implements it.

## Output Format

```
🧪 Tests for <function/file>:

[paste-ready snippet]

⚠️ Untestable: <reason>
   💡 Suggest: <refactor>

✅ Edge cases to add:
- [bullet]
- [bullet]
```

## When to say "already well-tested"

If the function is pure, simple, and existing tests cover it, say so plainly. Don't invent tests just to look thorough.
