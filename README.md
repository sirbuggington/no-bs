# no-bs

A Claude Code skill that turns off default sycophantic softening for the rest of the conversation.

While active, the assistant operates as a senior expert who tells the truth — including saying "this is good, ship it" when that's the honest answer. No manufactured concerns, no "you might want to consider…" hedges, no praise sandwich. It pushes back when you're wrong, agrees when you're right, and asks for clarification when it doesn't have enough context to do either.

The opposite of sycophantic. *Not* the same as adversarial — it doesn't disagree with you for sport.

## Install

### Option 1: Clone

```bash
git clone https://github.com/sirbuggington/no-bs.git ~/.claude/skills/no-bs
```

That's it. Restart Claude Code and the skill is available.

### Option 2: Download the single file

Download [SKILL.md](https://raw.githubusercontent.com/sirbuggington/no-bs/main/SKILL.md) and save it to:

- **Windows:** `C:\Users\<you>\.claude\skills\no-bs\SKILL.md`
- **macOS / Linux:** `~/.claude/skills/no-bs/SKILL.md`

(Create the `no-bs` folder if it doesn't exist.)

Restart Claude Code.

## Use

Once installed, invoke it in any chat:

```
/no-bs
```

Or just ask: "use the no-bs skill" / "enable no-bs mode".

The skill stays active for the rest of that conversation. There's no off-switch by design — to turn it off, start a new chat.

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

After installing, try this in a fresh chat with the skill enabled:

1. Pitch it an idea you actually like and want validated. See if it agrees, pushes back honestly, or manufactures fake concerns.
2. Push back on a piece of its criticism with "are you sure?" — see if it holds ground or folds.
3. Push back with an actual counter-argument that addresses the criticism — see if it concedes plainly.

If steps 1-3 all behave as described, the skill is working.

## Origin

Inspired by [mattpocock/grill-me](https://skills.sh/mattpocock/skills/grill-me), but different: grill-me is a Socratic interviewer for plans/designs only. no-bs changes tone for the entire conversation across all topics.

The spec went through two rounds of cross-model peer review (Codex caught real gaps in the first draft) before this SKILL.md was written.
