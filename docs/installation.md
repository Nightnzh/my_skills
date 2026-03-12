# Installation

## Preferred: installer script

Use the local installer script from a clone of this repository:

```bash
./tools/install_skill <slug>
./tools/install_skill <slug> --version 1.2.3
./tools/install_skill <slug> --target codex
./tools/install_skill --list
```

Defaults:

- `--target codex`
- target root: `$CODEX_HOME/skills` when `CODEX_HOME` is set
- fallback target root: `~/.codex/skills`

Deprecated skills require an explicit opt-in:

```bash
./tools/install_skill <slug> --allow-deprecated
```

## Supported: Git URL or clone workflow

You can also consume a skill directly from the repository:

1. Clone the repository.
2. Navigate to `skills/<slug>/`.
3. Point your host environment at that directory or copy it manually.
4. Optionally pin to a specific commit or tag in your own automation.

Use this path when you want full control over updates or want to review the skill contents before installation.
