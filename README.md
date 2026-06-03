# acm-debug

A Claude Code skill that performs systematic code debugging. It reads your file, works through every category of bug — critical errors, logic errors, potential issues, and code quality — and returns a structured report with line numbers, explanations, and ready-to-use fixes.

## What it does

| Category | Examples |
|----------|---------|
| 🔴 **Critical Errors** | Null dereferences, unhandled exceptions, infinite loops, race conditions |
| 🟡 **Logic Errors** | Off-by-one, inverted conditions, wrong operator precedence, float comparisons |
| 🟠 **Potential Issues** | Division by zero, missing input validation, resource leaks, injection vulnerabilities |
| 🔵 **Code Quality** | Dead code, unused variables, magic values, ignored errors |

Supports any language Claude Code can read: Python, JavaScript/TypeScript, Go, Rust, Java, C/C++, Ruby, PHP, and more.

---

## Requirements

- [Claude Code](https://claude.ai/code) (CLI, VS Code extension, or desktop app)

---

## Installation

### Option A — One-liner (recommended)

**macOS / Linux**
```bash
git clone https://github.com/acm-rgb/acm-systematic-debug.git
cd acm-systematic-debug
chmod +x install.sh

# Install into the current project
./install.sh

# Or install globally (available in every project)
./install.sh --global

# Or install into a specific project
./install.sh --project /path/to/your/project
```

**Windows (PowerShell)**
```powershell
git clone https://github.com/acm-rgb/acm-systematic-debug.git
cd acm-systematic-debug

# Install into the current project
.\install.ps1

# Or install globally
.\install.ps1 -Global

# Or install into a specific project
.\install.ps1 -Project C:\path\to\your\project
```

### Option B — Manual (copy one file)

Copy `commands/debug.md` into the `.claude/commands/` directory of your project:

```
your-project/
└── .claude/
    └── commands/
        └── debug.md   ← paste here
```

For global installation (available in all projects), copy it to:
- macOS/Linux: `~/.claude/commands/debug.md`
- Windows: `%USERPROFILE%\.claude\commands\debug.md`

---

## Usage

Once installed, open Claude Code inside your project and use the `/debug` command:

```
/debug src/auth.py
```

### Flags

| Flag | Description |
|------|-------------|
| _(none)_ | Full report — all four categories |
| `--quick` | Only Critical and Logic errors (faster for large files) |
| `--fix` | Full report + auto-apply Critical and Logic fixes to the file |
| `--lang <language>` | Override language detection (e.g., `--lang typescript`) |

### Examples

```bash
# Full analysis of a single file
/debug src/auth.py

# Quick scan — only show errors that will crash or misbehave
/debug lib/parser.js --quick

# Analyze and automatically fix critical + logic issues
/debug internal/server.go --fix

# Override language if the extension is ambiguous
/debug Makefile --lang bash
```

---

## Output format

```
## Debug Report: `src/auth.py`

Language detected: Python
Lines analyzed: 142

### Summary
The file implements JWT authentication. Found 2 critical errors, 1 logic error,
3 potential issues. Most urgent: uncaught KeyError on line 38.

---

### 🔴 Critical Errors — 2

| Line | Issue | Offending Code | Fix |
|------|-------|----------------|-----|
| L38 | KeyError — `payload["user_id"]` not guarded | `uid = payload["user_id"]` | Use `.get()`: `uid = payload.get("user_id")` |
| L91 | File handle never closed on exception path | `f = open(path)` | Use `with open(path) as f:` |

### 🟡 Logic Errors — 1
...

### Recommended Fixes
<before/after code blocks for each critical and logic error>

### Risk Assessment
| Field | Value |
|-------|-------|
| Overall severity | 🔴 Critical |
| Confidence | High |
| Estimated fix effort | < 30 min |
| Highest-priority action | Fix KeyError on L38 — can crash any authenticated request |
```

---

## How it works

The skill is a single markdown file (`.claude/commands/debug.md`) that Claude Code loads when you type `/debug`. It instructs Claude to:

1. Read the target file
2. Walk through each bug category systematically
3. Record every issue with its line number, a description, the offending code, and an exact fix
4. Output a structured table report
5. Optionally apply fixes in-place when `--fix` is passed

No external dependencies, no API keys, no configuration required.

---

## Contributing

Pull requests are welcome. To add a new check, edit `commands/debug.md` and add the rule under the appropriate category in Step 3.

---

## License

MIT
