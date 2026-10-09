# Hermes skills

This directory contains only my custom skill:

- `software-development/remind` — selective context routing through a Markdown vault.

The original frontmatter, scripts, and templates are preserved. Skills supplied by Hermes itself are not included. The export does not remove or reconfigure the installed Hermes skills.

## Privacy boundary

`remind` is exported as a reusable procedure, not as a copy of my personal knowledge base:

- The vault contains only empty starter indexes, without project knowledge or personal rules.
- The real interaction history is not exported; `templates/interaction-history.md` provides an empty starting file.
- Credentials, Hermes configuration, usage counters, curator state, and caches are excluded.
- `.gitignore` excludes local history and non-starter vault files. It cannot protect later edits to the tracked starter indexes: inspect staged changes before publishing.

## Installation

Copy `software-development/remind` into `$HERMES_HOME/skills/software-development/remind/` (by default `~/.hermes/skills/software-development/remind/`). Back up an existing installation first; do not overwrite your existing vault or history with these empty starters.

For a new `remind` installation, initialize local history once from its template:

```sh
remind_root="${HERMES_HOME:-$HOME/.hermes}/skills/software-development/remind"
if [ ! -e "$remind_root/references/interaction-history.md" ]; then
    mkdir -p "$remind_root/references"
    cp "$remind_root/templates/interaction-history.md" "$remind_root/references/interaction-history.md"
fi
```

Start a new Hermes session after installation. The skill is not installed, enabled, or linked automatically by this repository.

## Script checks

The Remind scripts use the Python standard library:

```sh
python3 skills/software-development/remind/scripts/context_review.py status
python3 skills/software-development/remind/scripts/append_history.py --help
```

Test history writes against an isolated copy, not the public package or an existing personal history. Do not commit generated history or personal vault contents.
