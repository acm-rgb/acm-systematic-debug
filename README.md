# acm-acm-systematic-debug

A [Claude Code](https://code.claude.com) / [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) skill that replaces guess-and-patch debugging with a disciplined, hypothesis-driven method for Python.

The default way coding agents (and people) debug is to read the error, guess a cause, and start editing. That fixes easy bugs and quietly makes hard ones worse — patching symptoms, introducing regressions, and leaving you with "it works now and I don't know why." This skill forces a method instead:

> **reproduce → observe → localize → hypothesize → test → verify → lock in**

Each step has a clear exit condition, and the skill explicitly refuses common anti-patterns (shotgun debugging, symptom patching, cargo-cult fixes, accepting fixes you can't explain).

## What's inside

```
acm-systematic-debug/
├── SKILL.md                          # the method + triggering rules
├── references/
│   └── python-bug-patterns.md        # field guide to 16 recurring Python bug families
└── scripts/
    └── repro.py                      # capture a structured failure report (no deps)
```

- **`SKILL.md`** — the debugging loop, the non-negotiables, anti-patterns to refuse, and a worked example. The frontmatter `description` controls when the agent auto-invokes the skill.
- **`references/python-bug-patterns.md`** — loaded on demand when a symptom matches a known family (mutable defaults, late-binding closures, dtype surprises, generator exhaustion, asyncio, and more). Each entry says how it shows up, the cause, and how to confirm it.
- **`scripts/repro.py`** — runs any command and captures exit code, stdout, stderr, and the parsed traceback (exception type, message, crash frame) in one clean report. Pure standard library.

```bash
python scripts/repro.py -- python path/to/script.py --flag value
python scripts/repro.py -- python -m pytest tests/test_foo.py -x
python scripts/repro.py --json -- python script.py     # machine-readable
```

## Install

**Claude Code** — copy the folder into your skills directory:

```bash
# project-level (this repo only)
cp -r acm-systematic-debug .claude/skills/

# or user-level (all your projects)
cp -r acm-systematic-debug ~/.claude/skills/
```

The skill then triggers automatically when you report a bug, paste a traceback, or have a failing test. You can also invoke it explicitly with `/acm-systematic-debug`.

**Other agents** — the `SKILL.md` format is an open standard, so the same folder works in Cursor, Gemini CLI, OpenAI Codex CLI, and others that have adopted it.

## Why it's structured this way

Skills use progressive disclosure: only the name + description sit in context until the skill is needed (~100 tokens), the body loads when it triggers, and `references/` is read only when relevant. That keeps the always-on cost tiny while making detailed knowledge available on demand — the `python-bug-patterns.md` guide doesn't cost anything until a bug actually matches one of its families.

## License

MIT — see [LICENSE](LICENSE).