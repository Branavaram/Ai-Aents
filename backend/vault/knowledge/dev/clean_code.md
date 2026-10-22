# Clean Code Principles (Summary)

> **Based on:** Robert C. Martin's "Clean Code" + Martin Fowler's "Refactoring"
> **Use:** Timeless code quality principles. Reference these when flagging smells.

## The Big Four Rules
1. **Runs all tests**
2. **No duplication** (DRY)
3. **Expresses intent of programmer**
4. **Minimizes classes and methods**
In that priority order.

## Meaningful Names
- **Intention-revealing:** `elapsed_time_in_days` not `d`
- **Avoid disinformation:** don't name an array `accountList` if it isn't a List
- **Pronounceable:** `generation_timestamp` not `genymdhms`
- **Searchable:** avoid `e`, prefer `event`
- **No encodings:** no Hungarian notation (`strName`)
- **Class names:** nouns (`Customer`, `WikiPage`)
- **Method names:** verbs (`postPayment`, `deletePage`)

## Functions
- **Small:** <20 lines, better <10
- **Do ONE thing**
- **One level of abstraction per function**
- **Few arguments:** 0 is best, 3+ is suspect
- **No flag arguments:** `render(isSuite)` → split into two methods
- **Prefer exceptions over error codes**
- **Don't repeat yourself**

## Comments
- **Good uses:**
  - Legal/informative headers
  - Explanation of intent that CAN'T be expressed in code
  - Warning of consequences
  - TODO (temporary)
  - Public API docs
- **Bad uses (DON'T):**
  - Comments that restate the code (`i++ // increment i`)
  - Commented-out code (delete it, git has history)
  - Journal comments (git has history)
  - Noise ("this function...")

## Formatting
- Smaller files are easier
- Related code goes together (vertical density)
- Variables declared close to where they're used
- Instance variables at the top of the class

## Objects and Data Structures
- Objects hide data, expose behavior
- Data structures expose data, no behavior
- **The Law of Demeter:** a method should only call methods of:
  - Its own class
  - Objects it created
  - Objects passed as arguments
  - Its instance variables
  Avoid: `account.getOwner().getAddress().getCity()`

## Error Handling
- **Use exceptions over return codes**
- **Write try-catch-finally first**
- **Provide context in exception messages**
- **Define exception classes by caller needs**
- **Don't return null** — return Optional/empty collection
- **Don't pass null** as argument

---

## Code Smells (Fowler)

### Within functions
- **Long Function** (>20 lines)
- **Long Parameter List** (>3)
- **Comments** explaining what code does (should rename instead)
- **Dead Code** (unreachable or unused)
- **Speculative Generality** (code "for the future" that's not needed now)

### Within classes
- **Large Class** (too many methods)
- **Lazy Class** (does too little)
- **Data Class** (just getters/setters, no behavior)
- **Feature Envy** (method uses another class's data more than its own)
- **Inappropriate Intimacy** (two classes know too much about each other)

### Between code
- **Duplicated Code** (same logic in multiple places)
- **Shotgun Surgery** (one change requires edits in many places)
- **Divergent Change** (one class changes for many reasons)
- **Primitive Obsession** (strings/ints where a small class would help)
- **Switch Statements** that recur with same cases
- **Parallel Inheritance Hierarchies**

### Design-level
- **God Class** (one class doing everything)
- **Golden Hammer** (one solution forced everywhere)
- **Vendor Lock-In** without abstraction
- **Dead End** (deprecated libraries)

---

## When reviewing, prioritize:
1. **Correctness** > Style
2. **Readability** > Cleverness
3. **Simplicity** > Flexibility
4. **Explicit** > Implicit

## Say "it works" first
If code is clear, correct, and does its job — approve it. Don't invent problems to look thorough. Perfect is the enemy of shipped.
