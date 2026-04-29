# no-bs

A Claude Code skill that turns off default sycophantic softening for the rest of the conversation. Real on/off toggle, no per-chat re-invocation needed.

While active, the assistant operates as a senior expert who tells the truth — including saying "this is good, ship it" when that's the honest answer. No manufactured concerns, no "you might want to consider…" hedges, no praise sandwich. It pushes back when you're wrong, agrees when you're right, and asks for clarification when it doesn't have enough context to do either.

The opposite of sycophantic. *Not* the same as adversarial — it doesn't disagree with you for sport.

## How it works

A `UserPromptSubmit` hook (`~/.claude/hooks/no-bs-route.py`) runs on every prompt. While `mode = "on"`, the hook injects a short tone-anchor reminder so Claude doesn't drift back to default behavior. While `mode = "off"`, the hook exits silently and Claude is unchanged.

The toggle is a flag file at `~/.claude/no-bs-mode.json`. `/no-bs on` and `/no-bs off` flip it. The hook reads it on every prompt — so the toggle takes effect immediately, persists across sessions, and only goes away if you uninstall.

## Install

You need Python 3.9+ already on your machine (`py -3 --version` on Windows, `python3 --version` on macOS/Linux).

```bash
git clone https://github.com/sirbuggington/no-bs.git
cd no-bs
```

Then run the installer:

- **Windows:** `py -3 install.py`
- **macOS / Linux:** `python3 install.py`

That's it. Restart Claude Code and `/no-bs` is available in any chat.

The installer is idempotent — safe to re-run after `git pull` to update.

### Preview before installing

```bash
python3 install.py --dry-run
```

Prints what it would do without changing anything.

### Uninstall

```bash
python3 install.py --uninstall
```

Removes the hook from `settings.json`, deletes the skill / hook / wrapper / mode file. Leaves your other settings untouched.

## Use

Once installed, no-bs is **on by default**. Every non-trivial prompt gets the tone-anchor.

```
/no-bs              show current mode
/no-bs status       same as above
/no-bs on           enable
/no-bs off          disable (hook stays installed but exits silently)
/no-bs help         show help
```

The state persists across sessions — `/no-bs off` stays off until you `/no-bs on` again.

### What gets skipped automatically (regardless of mode)

- Prompts starting with `/peer`, `/clarify`, or `/no-bs` (and `-*` variants) — those skills own those turns
- Prompts under 5 characters
- Pure acknowledgements: `thanks`, `ok`, `yes`, `hello`, etc.

## What it does

- **Agrees plainly when you're right.** "This works, ship it." is a successful response, not a lazy one.
- **Disagrees with specifics when you're wrong.** Names what's wrong and why, in language you can argue with.
- **Holds ground against social pressure.** Won't fold to "are you sure?" — only to actual counter-arguments (new evidence, false-premise correction, knowingly accepted tradeoff, narrowed goal).
- **Concedes plainly when you have a real counter.** Names what changed its view, doesn't bury the concession in qualifiers.
- **Calibrates by domain.** Direct but not cruel on emotional topics. Plain on factual lookups. Honest about tradeoffs but still produces what you asked for on code/creative requests.

## What it won't do

- No sarcasm or snark
- No lecturing or moralizing ("as a best practice…" speeches)
- No hedging that softens a confident claim ("you might want to consider…")
- No manufactured concerns to look thorough
- No performance of toughness — if the honest answer is boring, you get the boring honest answer

## How to test it

After installing, in a fresh chat:

1. `/no-bs status` — confirm it's on.
2. Pitch it an idea you actually like and want validated. See if it agrees plainly, pushes back honestly, or manufactures fake concerns.
3. Push back on a piece of its criticism with "are you sure?" — see if it holds ground or folds.
4. Push back with an actual counter-argument that addresses the criticism — see if it concedes plainly.
5. `/no-bs off` — try the same prompts. Tone should noticeably soften back to default.

## Files installed

| Path | Purpose |
|---|---|
| `~/.claude/skills/no-bs/SKILL.md` | Full behavior spec |
| `~/.claude/hooks/no-bs-route.py` | Per-prompt injector |
| `~/.claude/commands/no-bs.md` | Slash-command wrapper |
| `~/.claude/no-bs-mode.json` | Mode state (`on` / `off`) |
| `~/.claude/settings.json` | Patched to register the hook (other entries untouched) |

The hook fails open: if it crashes for any reason, your prompt still reaches Claude — worst case is the reminder doesn't fire, never that messages get swallowed.

## Origin

Inspired by [mattpocock/grill-me](https://skills.sh/mattpocock/skills/grill-me), but different: grill-me is a Socratic interviewer for plans/designs only. no-bs changes tone for the entire conversation across all topics.

The architecture (UserPromptSubmit hook + mode file + slash command wrapper) mirrors the same pattern used by Claude Code's `/clarify` skill, which is the right shape for any "always-on with toggle" behavior modifier.

The spec and reminder text both went through cross-model peer review (Codex caught real gaps) before being locked.
