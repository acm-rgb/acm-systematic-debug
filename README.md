# acm-systematic-debug

A [Claude Code](https://code.claude.com) skill that replaces guess-and-patch debugging with a disciplined, hypothesis-driven method for Python. Distributed as an installable plugin.

The default way coding agents (and people) debug is to read the error, guess a cause, and start editing. That fixes easy bugs and quietly makes hard ones worse — patching symptoms, introducing regressions, and leaving you with "it works now and I don't know why." This skill forces a method instead:

> **reproduce → observe → localize → hypothesize → test → verify → lock in**

Each step has a clear exit condition, and the skill explicitly refuses common anti-patterns (shotgun debugging, symptom patching, cargo-cult fixes, accepting fixes you can't explain).

## Install

Clone and copy

If you'd rather not use the marketplace:

```bash
git clone https://github.com/acm-rgb/acm-systematic-debug.git
cp -r acm-systematic-debug/skills/acm-systematic-debug ~/.claude/skills/   # all projects
# or .claude/skills/ for the current project only
```

The same `SKILL.md` format is an open standard, so the skill folder also works in Cursor, Gemini CLI, and OpenAI Codex CLI.

## What's inside

```
acm-systematic-debug/
├── .claude-plugin/
│   ├── plugin.json                       # plugin manifest
│   └── marketplace.json                  # marketplace manifest (makes /plugin install work)
├── skills/
│   └── acm-systematic-debug/
│       ├── SKILL.md                      # the method + triggering rules
│       ├── references/
│       │   └── python-bug-patterns.md    # field guide to 16 recurring Python bug families
│       └── scripts/
│           └── repro.py                  # capture a structured failure report (no deps)
├── README.md
└── LICENSE
```

- **`SKILL.md`** — the debugging loop, the non-negotiables, anti-patterns to refuse, and a worked example. The frontmatter `description` controls when the agent auto-invokes the skill.
- **`references/python-bug-patterns.md`** — loaded on demand when a symptom matches a known family (mutable defaults, late-binding closures, dtype surprises, generator exhaustion, asyncio, and more).
- **`scripts/repro.py`** — runs any command and captures exit code, stdout, stderr, and the parsed traceback (exception type, message, crash frame) in one clean report. Pure standard library.

```bash
python scripts/repro.py -- python path/to/script.py --flag value
python scripts/repro.py -- python -m pytest tests/test_foo.py -x
python scripts/repro.py --json -- python script.py     # machine-readable
```

## Why it's structured this way

Skills use progressive disclosure: only the name + description sit in context until the skill is needed (~100 tokens), the body loads when it triggers, and `references/` is read only when relevant. That keeps the always-on cost tiny while making detailed knowledge available on demand.

## License

MIT — see [LICENSE](LICENSE).