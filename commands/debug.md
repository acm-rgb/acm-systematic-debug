---
description: Systematic code debugger — finds bugs, logic errors, and potential issues with structured reports and fix suggestions
---

Analyze code for bugs and errors. Arguments: $ARGUMENTS

## Step 1 — Identify the Target

Parse `$ARGUMENTS`:
- If it is a file path (e.g., `src/app.py`, `./utils.js`), read the file using the Read tool.
- If it contains inline code or is a code snippet, analyze it directly.
- If it is empty, ask the user: "What file or code should I debug? You can pass a file path or paste code directly."
- Flags to handle:
  - `--quick`: report only Critical and Logic errors, skip Potential and Quality sections.
  - `--fix`: after the report, apply all Critical and Logic fixes directly to the file using the Edit tool.
  - `--lang <language>`: override language detection.

## Step 2 — Detect Language

Infer the programming language from the file extension or syntax. Use this to apply language-specific checks listed in Step 3.

## Step 3 — Systematic Analysis

Work through each category below in order. Do NOT skip categories. For each issue found, record: line number (or range), category, a one-sentence description, the offending code, and the recommended fix.

### 🔴 Category 1: Critical Errors
These will cause crashes, exceptions, or data corruption at runtime.

- **Null / undefined dereferences** — accessing a property or calling a method on a value that can be null/undefined/nil/None without a prior guard.
- **Unhandled exceptions** — calls that can throw (file I/O, network, parsing) with no try/catch or equivalent.
- **Infinite loops** — loops with no reachable exit condition, or recursive functions with no base case.
- **Memory safety** (C/C++/Rust) — buffer overflows, use-after-free, double-free, out-of-bounds writes.
- **Concurrency / race conditions** — shared mutable state accessed from multiple goroutines/threads/coroutines without synchronization.
- **Type errors** — passing the wrong type where a crash is guaranteed (e.g., calling a non-function, arithmetic on strings in typed languages).
- **Missing return** — function declared to return a value but has a code path that returns nothing.

### 🟡 Category 2: Logic Errors
The code runs but produces wrong results.

- **Off-by-one errors** — loop bounds `< n` vs `<= n`, slice indices, array access at `length` instead of `length - 1`.
- **Inverted conditions** — `===` vs `!==`, `>` vs `<`, wrong boolean operators (`&&` vs `||`).
- **Wrong operator precedence** — expressions evaluated in unintended order without explicit parentheses.
- **Incorrect algorithm** — sorting that doesn't sort, accumulator not reset between iterations, wrong formula.
- **Shadowed variables** — inner scope variable with same name masking outer scope, causing silent wrong reads.
- **Mutating while iterating** — modifying a collection inside a loop that iterates over it.
- **Floating-point comparison** — using `==` to compare floats instead of an epsilon check.
- **Integer vs float division** — `5 / 2 = 2` in languages where `/` truncates for integers.

### 🟠 Category 3: Potential Issues
Won't always fail, but will under specific inputs or conditions.

- **Division by zero** — divisor can be zero under certain inputs with no guard.
- **Integer overflow / underflow** — arithmetic that can exceed the type's range.
- **Array / index out of bounds** — access guarded only by a condition that doesn't cover all paths.
- **Missing input validation** — user-supplied or external data used directly without type/range/format checks.
- **Resource leaks** — file handles, DB connections, sockets opened but not closed in all paths (including error paths).
- **SQL injection / command injection** — external input interpolated directly into queries or shell commands.
- **Deprecated or unsafe APIs** — use of known-unsafe functions (`strcpy`, `eval`, `pickle.loads` on untrusted data, etc.).

### 🔵 Category 4: Code Quality
Not bugs, but increase the likelihood of future bugs.

- **Dead code** — unreachable branches, unused functions/methods/classes.
- **Unused variables / imports** — declared or imported but never read.
- **Hardcoded magic values** — literal numbers or strings that should be named constants.
- **Missing error propagation** — error returned by a callee is silently ignored.
- **Overly complex conditions** — nested ternaries or boolean expressions that are hard to reason about.

## Step 4 — Output the Report

Use exactly this format. Omit any table that has zero rows (write "None found." instead). Always include the Summary and Risk Assessment sections.

---

## Debug Report: `<filename or "Code Snippet">`

**Language detected:** `<language>`
**Lines analyzed:** `<n>`

### Summary
<One paragraph: what the code does, total issues found per category, and the single most important thing to fix.>

---

### 🔴 Critical Errors — <count>

| Line | Issue | Offending Code | Fix |
|------|-------|----------------|-----|
| L12 | Null dereference on `user.name` | `return user.name.toUpperCase()` | Add guard: `return user?.name?.toUpperCase() ?? ""` |

<If count is 0, write: "None found.">

---

### 🟡 Logic Errors — <count>

| Line | Issue | Offending Code | Fix |
|------|-------|----------------|-----|

<If count is 0, write: "None found.">

---

### 🟠 Potential Issues — <count>

| Line | Issue | Offending Code | Fix |
|------|-------|----------------|-----|

<If count is 0, write: "None found.">

---

### 🔵 Code Quality — <count>

| Line | Issue | Offending Code | Fix |
|------|-------|----------------|-----|

<If count is 0, write: "None found.">

---

### Recommended Fixes

For every Critical and Logic error, show a before/after diff or the corrected code block. Label each fix with its line number and a one-sentence explanation of WHY the original was wrong.

```<language>
// Before — L12: user.name can be null when user was fetched without the profile relation
return user.name.toUpperCase()

// After
return user?.name?.toUpperCase() ?? ""
```

---

### Risk Assessment

| Field | Value |
|-------|-------|
| **Overall severity** | 🔴 Critical / 🟡 High / 🟠 Medium / 🔵 Low |
| **Confidence** | High / Medium / Low |
| **Estimated fix effort** | < 30 min / 1–2 h / Half day / Full day |
| **Highest-priority action** | <single most important next step> |

---

## Step 5 — Apply Fixes (only when `--fix` flag is present)

If `--fix` was passed:
1. Apply every Critical and Logic fix using the Edit tool.
2. After all edits, print a short list of what was changed.
3. Do NOT apply Potential or Quality fixes automatically — mention them as "manual review required."

## Step 6 — Follow-up

After the report, offer two options:
- "Run `/debug --fix <file>` to apply all Critical and Logic fixes automatically."
- "Ask me about any specific issue for a deeper explanation or alternative fix."
