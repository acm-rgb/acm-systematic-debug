---
name: acm-systematic-debug
description: Apply a rigorous, hypothesis-driven method to debug Python code instead of guessing and patching at random. Use this whenever the user reports a bug, pastes a traceback or error message, has a failing test, gets unexpected output, or says Python code "broke", "isn't working", "crashes", or "returns the wrong thing" — even when they only paste an error with no question. Resist jumping straight to a fix; this skill enforces reproduce → isolate → hypothesize → test → verify so the real root cause gets found and a regression test gets added.
---

# Systematic Debug (Python)

The default failure mode when debugging — for humans and models alike — is to read the error, guess a cause, and start changing code. That works on easy bugs and fails badly on everything else: it fixes symptoms instead of causes, introduces new bugs, and leaves you with "it works now and I don't know why."

This skill replaces guessing with a disciplined loop. Follow it in order. Do not skip to the fix.

## The non-negotiables

1. **Never debug what you can't reproduce.** A bug you can't trigger on demand cannot be confirmed fixed. Get a reliable reproduction first.
2. **Read the actual error before theorizing.** The traceback names the file, line, and exception. Gather facts before forming opinions.
3. **Change one thing at a time.** Each change must test exactly one hypothesis. Changing several things at once means you won't know what fixed it — or what broke next.
4. **Every hypothesis must be falsifiable.** State what you expect to happen *before* you run, then compare. "Let me try this and see" is not a hypothesis.
5. **A fix isn't done until the reproduction passes and a regression test exists.** Otherwise the bug comes back.

## The loop

### 1. Reproduce
Get a minimal, reliable trigger for the bug.
- Ask for / construct the smallest input and command that produces it.
- Confirm it fails consistently. If it's intermittent, note that explicitly — flaky bugs need extra attention to ordering, timing, state, and randomness (seed it).
- Use `scripts/repro.py` to run a command and capture stdout, stderr, exit code, and the full traceback into one clean report. See "Tooling" below.

### 2. Observe
Read the failure completely before changing anything.
- Read the **entire** traceback, bottom to top: the bottom frame is where it blew up, the frames above show how it got there.
- Note the exception **type** and **message** — they usually point straight at the category of bug.
- State the gap in one sentence: "Expected X, got Y."

### 3. Localize
Narrow down *where* the fault is before asking *why*.
- Binary-search the failure: does the bad value exist halfway through the pipeline? Bisect until you've cornered the smallest region of code that still reproduces it.
- For "it used to work," bisect history (`git bisect`) to find the commit that introduced it.
- Inspect state at the boundary you've cornered: print/log the relevant variables, or drop a `breakpoint()` and inspect live.

### 4. Hypothesize
Form **one** specific, falsifiable claim about the cause.
- Good: "`total` is a string because `read_csv` left the column as object dtype, so `+` concatenates instead of adding."
- Bad: "Something's wrong with the data."
- If you have several candidates, rank them by likelihood and test the most likely first.

### 5. Test the hypothesis
- Predict the outcome out loud: "If I'm right, casting to int will make the sum 42, not '42'."
- Make the **single** smallest change that tests it.
- Run the reproduction. Did reality match the prediction?
  - **Yes** → you've found the cause. Go to step 6.
  - **No** → the hypothesis is wrong. Revert the change (don't leave it lying around) and return to step 4 with what you learned.

### 6. Fix and verify
- Apply the **minimal** fix that addresses the root cause — not the symptom. (Catching the exception to hide it is almost never the fix.)
- Re-run the reproduction: it must now pass.
- Run the surrounding tests / adjacent functionality to check you didn't break anything else.

### 7. Lock it in
- Write a regression test that fails on the old code and passes on the fixed code. This is what stops the bug returning.
- State the root cause in one sentence so the user understands *why* it happened, not just that it's fixed.

## Anti-patterns to refuse

- **Shotgun debugging** — changing many things hoping one works. Stop; isolate one variable.
- **Symptom patching** — wrapping in `try/except`, adding `if x is None` guards, or `# noqa` to silence the error without understanding it.
- **Cargo-cult fixes** — copying a Stack Overflow snippet because it's vaguely related.
- **Accepting "it works now"** — if you can't explain *why* the fix works, you haven't finished step 5.
- **Debugging without reproducing** — theorizing about a bug you can't trigger.

When you catch yourself (or the user) doing any of these, name it and return to the loop.

## Tooling

`scripts/repro.py` runs a Python command and captures a structured failure report (exit code, stdout, stderr, parsed traceback) — useful for getting clean facts in step 1 and confirming the fix in step 6:

```bash
python scripts/repro.py -- python path/to/failing_script.py --some-arg
python scripts/repro.py -- python -m pytest tests/test_foo.py::test_bar -x
```

Native Python tools to reach for:
- `breakpoint()` — drops into pdb at that line (set `PYTHONBREAKPOINT=0` to disable, or point it at another debugger).
- `python -m pytest -x --pdb` — stop at first failure and open a debugger at the failure point.
- `python -X faulthandler` / `import faulthandler` — dumps a traceback on segfault or hang.
- `import traceback; traceback.print_exc()` — full stack inside an except block.
- `python -m pdb script.py` — step through from the start.
- `py-spy dump --pid <pid>` — see what a hung/slow process is doing without modifying it.
- `tracemalloc` — track memory growth for leaks.

## Python-specific bug patterns

Many Python bugs fall into a handful of recurring categories (mutable default arguments, late-binding closures, dtype surprises, encoding, scope, circular imports, generator exhaustion, asyncio gotchas, floating-point). When the symptom matches one of these families, read **`references/python-bug-patterns.md`** — it lists each pattern, how it shows up, and how to confirm it. Consult it in step 4 when forming a hypothesis.

## Example walkthrough

**User:** "My function returns 0 sometimes and I have no idea why."

Wrong move: scan the function and guess.

Right move:
1. **Reproduce** — ask for an input that returns 0; confirm it's consistent for that input.
2. **Observe** — no exception, just wrong value. Gap: "Expected a positive total, got 0."
3. **Localize** — log the value at each step; find it's already 0 right after the loop.
4. **Hypothesize** — "The loop never executes because the iterator was already consumed upstream."
5. **Test** — predict: if I materialize the iterator to a list first, the loop runs. Make that one change, run → total is now correct. Hypothesis confirmed.
6. **Fix** — accept a list, or document that the function consumes the iterator; re-run reproduction.
7. **Lock in** — regression test passing a generator. Root cause: generators are single-pass and were exhausted by an earlier `sum()`.