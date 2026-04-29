---
name: no-bs
description: /no-bs — manage the always-on brutal-honesty rule. Switches the hook on/off or shows current status. While on, every non-trivial prompt gets a tone-anchor reminder so Claude doesn't drift back to default sycophantic patterns. Equivalent to typing /no-bs <subcommand>. Read-only when called with no args or `status`.
argument-hint: [on | off | status | help]
---

This is a wrapper that delegates to the main /no-bs skill.

When invoked with /no-bs <args>, treat the invocation as if the user typed
/no-bs <args> and follow the rules in ~/.claude/skills/no-bs/SKILL.md exactly.
Same mode-file format, same slash-command grammar, same fail-open behavior.

If the main /no-bs skill is not installed at ~/.claude/skills/no-bs/, abort with:

    /no-bs wrapper requires the no-bs skill at ~/.claude/skills/no-bs/.
    The skill ships with the hook at ~/.claude/hooks/no-bs-route.py and the
    mode file at ~/.claude/no-bs-mode.json.
