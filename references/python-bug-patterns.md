# Python Bug Patterns

A field guide to recurring Python bug families. When a symptom matches one of these, you have a strong hypothesis candidate (step 4 of the loop). Each entry: how it shows up, the cause, and how to confirm.

## Contents
1. Mutable default arguments
2. Late-binding closures
3. Integer / float / dtype surprises
4. `is` vs `==`
5. Mutable shared state / aliasing
6. Scope and `UnboundLocalError`
7. Circular imports
8. Generator / iterator exhaustion
9. Dictionary ordering and mutation during iteration
10. Exceptions silently swallowed
11. Floating-point comparison
12. Encoding / bytes vs str
13. Off-by-one and slicing
14. `None` propagation
15. asyncio gotchas
16. Shadowing builtins / modules

---

## 1. Mutable default arguments
**Symptom:** A list/dict/set default "remembers" values across calls; the function accumulates state it shouldn't.
**Cause:** Default arguments are evaluated **once**, at definition time. `def f(x, acc=[])` shares one list across all calls.
**Confirm:** Call the function twice with no argument and check whether the second call sees the first call's data.
**Fix:** Use `None` as the sentinel: `def f(x, acc=None): acc = [] if acc is None else acc`.

## 2. Late-binding closures
**Symptom:** A list of functions (often built in a loop) all return the same value — usually the last one.
**Cause:** Closures capture the **variable**, not its value at creation time. By the time they run, the loop variable has its final value.
**Confirm:** `funcs = [lambda: i for i in range(3)]; [f() for f in funcs]` → `[2, 2, 2]`.
**Fix:** Bind via default arg `lambda i=i: i`, or use `functools.partial`.

## 3. Integer / float / dtype surprises
**Symptom:** Arithmetic gives wrong results; `+` concatenates instead of adding; pandas column won't sum.
**Cause:** A value is a `str` (or pandas `object`/wrong dtype) when you assumed numeric. `"2" + "2" == "22"`.
**Confirm:** `type(x)` on the suspect value; `df.dtypes` for a DataFrame.
**Fix:** Cast explicitly (`int()`, `float()`, `pd.to_numeric`), and fix the source that produced the wrong type.

## 4. `is` vs `==`
**Symptom:** A comparison that "should" be true is false, or vice versa — often with small ints, strings, or `None`.
**Cause:** `is` checks identity (same object), `==` checks equality. CPython caches small ints (-5..256) and some strings, so `is` *sometimes* works by accident, then fails for larger values.
**Confirm:** Replace `is` with `==` (except for `None`, `True`, `False`, where `is` is correct) and see if the bug disappears.
**Fix:** Use `==` for value comparison; reserve `is` for singletons.

## 5. Mutable shared state / aliasing
**Symptom:** Changing one variable unexpectedly changes another; a copy isn't really a copy.
**Cause:** `b = a` binds another name to the same object. `list2 = list1[:]` copies one level only — nested objects are still shared (shallow copy).
**Confirm:** `id(a) == id(b)`; mutate a nested element and check both.
**Fix:** `copy.deepcopy` when you need full independence; be deliberate about shallow vs deep.

## 6. Scope and `UnboundLocalError`
**Symptom:** `UnboundLocalError: local variable 'x' referenced before assignment`, even though `x` exists at module level.
**Cause:** Assigning to a name anywhere in a function makes it local for the **whole** function, shadowing the outer one before it's assigned.
**Confirm:** Look for an assignment to that name later in the function.
**Fix:** `global`/`nonlocal` if you truly mean the outer variable, or rename the local.

## 7. Circular imports
**Symptom:** `ImportError: cannot import name X` or `partially initialized module`, only at startup.
**Cause:** Module A imports B at top level while B imports A — one runs before the other is fully defined.
**Confirm:** Trace the import chain; the traceback shows the cycle.
**Fix:** Move the import inside the function that needs it, merge the modules, or extract the shared piece into a third module.

## 8. Generator / iterator exhaustion
**Symptom:** A loop or `sum`/`list` over something yields nothing the second time; counts come out as 0.
**Cause:** Generators and `map`/`filter`/`zip` objects are single-pass. Once consumed, they're empty.
**Confirm:** `list(gen)` twice — second is `[]`.
**Fix:** Materialize to a list if you need to iterate more than once, or recreate the generator.

## 9. Dict ordering and mutation during iteration
**Symptom:** `RuntimeError: dictionary changed size during iteration`, or items skipped.
**Cause:** Adding/removing keys while iterating a dict (or set).
**Confirm:** Look for `del`/assignment inside a `for k in d:` loop.
**Fix:** Iterate over `list(d.keys())` / `list(d.items())`, or build a new dict.

## 10. Exceptions silently swallowed
**Symptom:** Code "does nothing" with no error; failures vanish.
**Cause:** A bare `except:` or `except Exception: pass` hides the real error (sometimes including `KeyboardInterrupt`/`SystemExit` with bare except).
**Confirm:** Temporarily narrow or remove the except and re-run; add `traceback.print_exc()` inside it.
**Fix:** Catch the specific exception you expect; never swallow silently.

## 11. Floating-point comparison
**Symptom:** `0.1 + 0.2 == 0.3` is `False`; sums drift.
**Cause:** Binary floating point can't represent most decimals exactly.
**Confirm:** Print with `repr()` to see full precision.
**Fix:** `math.isclose(a, b)` for comparison; `decimal.Decimal` or integer cents for money.

## 12. Encoding / bytes vs str
**Symptom:** `UnicodeDecodeError`, `TypeError: a bytes-like object is required`, mojibake.
**Cause:** Mixing `bytes` and `str`, or reading a file with the wrong encoding.
**Confirm:** `type()` the value; check the file's actual encoding.
**Fix:** Decode/encode explicitly with the right codec; open text files with `encoding="utf-8"`.

## 13. Off-by-one and slicing
**Symptom:** First or last element missing/duplicated; `IndexError`.
**Cause:** Python slices are half-open (`a[i:j]` excludes `j`); ranges exclude the stop; indexing is 0-based.
**Confirm:** Check the boundary values by hand for a tiny input.
**Fix:** Reason explicitly about inclusive/exclusive bounds.

## 14. `None` propagation
**Symptom:** `AttributeError: 'NoneType' object has no attribute ...` far from the real cause.
**Cause:** A function returned `None` (often an in-place method like `list.sort()` that returns None, or a missing `return`) and it flowed downstream.
**Confirm:** Walk back up the traceback to where the value first became `None`.
**Fix:** Return the value you meant to; don't assign the result of in-place methods.

## 15. asyncio gotchas
**Symptom:** "coroutine was never awaited"; code returns a coroutine object instead of a result; nothing runs.
**Cause:** Calling an `async def` without `await`, blocking the event loop with sync I/O, or forgetting `asyncio.run`.
**Confirm:** Check for warnings about un-awaited coroutines; inspect return types.
**Fix:** `await` coroutines; use async-native libraries for I/O inside the loop.

## 16. Shadowing builtins / modules
**Symptom:** `TypeError: 'list' object is not callable`, or your own `random.py` import does nothing expected.
**Cause:** A variable named `list`, `dict`, `str`, `id`, `type`, etc., shadows the builtin; or a local file shares a stdlib module's name.
**Confirm:** Search for assignments to builtin names; check for local files matching imported module names.
**Fix:** Rename the variable/file.