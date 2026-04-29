# no-bs-route.py
# UserPromptSubmit hook for the /no-bs skill.
#
# Always-on enforcement layer for "brutal-honest response mode" — the user-facing
# contract is: while no-bs is on, every response is direct, specific, and
# non-sycophantic. Honest agreement is a success state. Hold ground against
# social pressure but concede to real counter-arguments.
#
# This hook injects a short tone-anchor on every non-trivial prompt while
# mode == "on". The full behavior spec lives in ~/.claude/skills/no-bs/SKILL.md
# and is referenced (not duplicated) in the injection.
#
# Hook decisions:
#   1. Skip on /peer*, /clarify*, /no-bs* invocations (avoid double-injection)
#   2. Skip if mode == "off"
#   3. Skip if prompt is trivially short (< 5 chars)
#   4. Skip if prompt is a pure acknowledgement (exact-match against ACK_LIST)
#   5. Otherwise inject the reminder
#
# Output schema: https://docs.claude.com/en/docs/claude-code/hooks
#
# Failure mode: this hook fails OPEN. Any error path exits 0 with no output so
# the user's prompt always reaches Claude. Better to lose the override on a
# rare parse failure than to silently swallow a user message.

import json
import os
import re
import sys
from pathlib import Path

# Python 3.9+ required
if sys.version_info < (3, 9):
    sys.exit(0)  # fail-open

if hasattr(sys.stdin, 'reconfigure'):
    sys.stdin.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


# Resolve config dir from CLAUDE_CONFIG_DIR (Claude Code's documented relocation
# env var) with ~/.claude as the fallback. Hook and the /no-bs slash command
# must agree on this path or they'll write to one file and read from another.
CLAUDE_CONFIG_DIR = Path(
    os.environ.get('CLAUDE_CONFIG_DIR') or os.path.expanduser('~/.claude')
)
NO_BS_MODE_FILE = CLAUDE_CONFIG_DIR / 'no-bs-mode.json'

DEFAULT_MODE = 'on'
VALID_MODES = ('on', 'off')

# Pure acknowledgements — case-insensitive exact match against the stripped
# prompt. The hook skips these because they're conversational filler, not task
# starts. Same list as clarify-route.py for consistency.
ACK_LIST = frozenset({
    'hello', 'hi', 'hey', 'yo',
    'thanks', 'thank you', 'thx', 'ty',
    'ok', 'okay', 'k', 'kk',
    'yes', 'yep', 'yeah', 'yup',
    'no', 'nope', 'nah',
    'cool', 'nice', 'lol',
    'alright', 'all right', 'sounds good',
    'got it', 'understood', 'done', 'perfect',
})

# Reminder text — locked via Codex peer review (round 1 AGREE).
# Source: .agent-work/codex-responses/XR-no-bs-reminder-design-plan-r1.md
INJECTION_TEXT = (
    "**[no-bs active]**\n\n"
    "For this response, be direct and specific. Honest agreement is a "
    "success state — don't manufacture concerns to look thorough. When "
    "pushed back on, hold ground unless the pushback adds new evidence, "
    "corrects a false premise, knowingly accepts a tradeoff, or narrows "
    "the goal. No hedging softeners. No sarcasm. No lectures. Ask when "
    "context is missing — that's honest uncertainty, not hedging.\n\n"
    "Full spec is already loaded: ~/.claude/skills/no-bs/SKILL.md."
)


def read_mode() -> str:
    """Return the current no-bs mode. Falls back to DEFAULT_MODE on any error."""
    try:
        if not NO_BS_MODE_FILE.exists():
            return DEFAULT_MODE
        data = json.loads(NO_BS_MODE_FILE.read_text(encoding='utf-8'))
        mode = data.get('mode', DEFAULT_MODE)
        if mode not in VALID_MODES:
            return DEFAULT_MODE
        return mode
    except Exception:
        return DEFAULT_MODE


def should_inject(prompt: str, mode: str) -> bool:
    """Decide whether to inject the no-bs reminder for this prompt.

    Gate:
      - mode != off
      - prompt non-trivial (>= 5 chars after strip)
      - prompt isn't a pure acknowledgement
    """
    if mode == 'off':
        return False

    stripped = prompt.strip()
    if len(stripped) < 5:
        return False

    # Strip trailing punctuation for ack matching ("ok!", "thanks." etc. should match)
    ack_candidate = stripped.rstrip('.!?,;:').lower()
    if ack_candidate in ACK_LIST:
        return False

    return True


def main() -> None:
    raw = sys.stdin.read()
    if not raw or not raw.strip():
        sys.exit(0)

    # Strip UTF-8 BOM if present
    raw = raw.lstrip('﻿')

    try:
        payload = json.loads(raw)
    except Exception:
        sys.exit(0)

    prompt = payload.get('prompt', '')
    if not isinstance(prompt, str):
        prompt = str(prompt) if prompt is not None else ''
    if not prompt or not prompt.strip():
        sys.exit(0)

    # Skip /peer* invocations — peer-route.py handles those.
    if re.search(r'^\s*/peer($|\s|-\w)', prompt, re.IGNORECASE):
        sys.exit(0)

    # Skip /clarify* invocations — clarify owns those turns.
    if re.search(r'^\s*/clarify($|\s|-\w)', prompt, re.IGNORECASE):
        sys.exit(0)

    # Skip /no-bs* invocations — the skill itself owns those turns.
    if re.search(r'^\s*/no-bs($|\s|-\w)', prompt, re.IGNORECASE):
        sys.exit(0)

    mode = read_mode()
    if not should_inject(prompt, mode):
        sys.exit(0)

    result = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": INJECTION_TEXT,
        }
    }

    print(json.dumps(result, separators=(',', ':'), ensure_ascii=False))


try:
    main()
except Exception:
    sys.exit(0)
