# acm-debug — Claude Code Slash Command Repository

This repository distributes the `acm-debug` slash command for Claude Code. Its only artifact is `commands/debug.md`.

## Repository layout

```
commands/
  debug.md      ← the slash command (only file that gets installed)
install.sh      ← Unix/macOS installer
install.ps1     ← Windows PowerShell installer
README.md       ← user-facing documentation
CLAUDE.md       ← this file
```

## Working on the slash command

The slash command lives entirely in `commands/debug.md`. It is a Claude Code custom command definition (`.claude/commands/`). To test changes:

1. Copy the file into a test project: `.claude/commands/debug.md`
2. Open that project in Claude Code
3. Run `/debug <some-file>` and verify the output format matches the report template

## Command design rules

- The output tables must always have columns: `Line | Issue | Offending Code | Fix`
- Categories are always printed in order: Critical → Logic → Potential → Quality
- Zero-issue categories say "None found." — never omit the section header
- `--fix` only auto-edits Critical and Logic; Potential and Quality require manual review
- Language detection is always stated explicitly in the report header

## Install scripts

Both scripts accept the same three modes: project (default), global, and explicit path. Keep them in sync when changing behavior.
