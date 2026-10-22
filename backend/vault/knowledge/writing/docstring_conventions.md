# Docstring & Documentation Conventions

> **Sources:**
> - [PEP 257](https://peps.python.org/pep-0257/)
> - [Google Python Style Guide — Comments](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
> - [Google Developer Documentation Style Guide](https://developers.google.com/style)

## When docstrings are REQUIRED
- Every **module**
- Every **public function/method** (not leading underscore)
- Every **public class**
- Every **public method**

## When docstrings are OPTIONAL
- Private helpers (`_prefixed`)
- Trivial one-liners (`def is_empty(x): return not x`)
- Properties that are self-explanatory

## The 3 Popular Styles

### Google style (recommended)
```python
def fetch_user(user_id: int, include_posts: bool = False) -> User:
    """Fetch a user from the database.

    Args:
        user_id: The user's unique integer ID. Must be positive.
        include_posts: If True, eager-load the user's posts.

    Returns:
        A User object with populated fields.

    Raises:
        UserNotFoundError: If no user exists with the given ID.
        ValueError: If user_id is not positive.
    """
```

### NumPy style
```python
def fetch_user(user_id, include_posts=False):
    """Fetch a user from the database.

    Parameters
    ----------
    user_id : int
        The user's unique integer ID.
    include_posts : bool, optional
        If True, eager-load the user's posts.

    Returns
    -------
    User
        A User object.

    Raises
    ------
    UserNotFoundError
        If no user exists.
    """
```

### Sphinx style (rST)
```python
def fetch_user(user_id, include_posts=False):
    """Fetch a user.

    :param user_id: User's ID.
    :type user_id: int
    :param include_posts: Include posts?
    :returns: A User object.
    :raises UserNotFoundError: No such user.
    """
```

**Google style is the most popular in modern Python** — recommend it unless the project uses another.

## Rules for all styles

### First line
- A **short summary** (<80 chars)
- Imperative mood: "Return" not "Returns"
- Ends with a period
- Blank line after if there's more

### Grammar in docs
- Second person is friendlier: "Enter your name" not "User enters their name"
- Use present tense: "Returns a list" not "Will return a list"
- Avoid: "simply", "just", "obviously", "trivially" — if it were obvious, it wouldn't need a doc

## README & Markdown Documentation

### Great README structure
```
# Project Name
> One-line value prop

## What it does
2-3 sentences, concrete.

## Quick Start
Install → config → run (3 steps max)

## Features
Bullets, scanable

## Usage examples
Real code snippets

## API reference
OR link to full docs

## Contributing
How to help

## License
```

### Markdown style
- One `#` H1 per file (the title)
- Code blocks ALWAYS specify language
- Links: descriptive text, not "click here"
- Tables for comparisons
- Admonitions (`> **Note:**`) for callouts

---

## When reviewing docs, flag:
1. Public functions with no docstring
2. Docstrings that just restate the function name
3. Params listed in docstring that don't match actual signature
4. Mixing docstring styles within one project
5. Jargon without definition on first use
6. Stale examples that reference removed code
7. "TODO" comments older than 3 months (likely abandoned)

## When reviewing writing, prefer:
- Short sentences over long
- Active voice over passive
- Concrete examples over abstract rules
- Second person ("you") over third ("the user")
- Plain words ("use") over fancy ones ("utilize")
