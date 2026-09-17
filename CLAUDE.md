# CLAUDE.md — manim-voiceover

Machine-facing notes for this repo. The reasoning behind it lives in an Obsidian vault.

## Check the vault first

**Before starting non-trivial work, read the vault.** It is at
`C:\Projects\personal-project-knowledge-vault\manim-voiceover\`
(repo: `github.com/F3rNaNDEZ57/personal-project-knowledge-vault`, private).

| Read | When |
|---|---|
| `Home.md` | Always — the entry point, with a numbered "Start here" |
| `System Map.md` + `.canvas` | Always — current status, next action, what is verified vs. merely built |
| `Open Decisions.md` | **Before any design choice.** `D1..Dn`, with the options that were rejected and why. Authoritative |
| `Roadmap.md` | Before picking up work — says what is done, deferred, and deliberately not being done |
| `Research Brief.md` | Before changing the generation approach — the failure taxonomy and what would falsify the design |
| `Runs/` | Before claiming something works — dated logs of what actually ran |
| `Skills/Skill Registry.md` | Before suggesting any third-party skill or a TTS change |

**Why this matters here:** this repo has already shipped documentation that contradicted its own
code (a README describing a local-TTS `jq` pipeline that never existed). The vault is the record
of what is actually true, including the things that were tried and rejected. Re-deriving a
settled decision wastes a turn; re-opening one without reading why it was settled is worse.

Two standing consequences recorded there, so they are not rediscovered the hard way:

- **Do not reintroduce a subprocess orchestrator** (D1).
- **Do not propose a third-party skill for text-to-speech** — 404 were surveyed, 16 audited, none
  can replace `GTTSService`. Better narration is a one-line `self.set_speech_service(...)` swap
  (`Skills/Skill Registry.md`).

## What this project is

Markdown maths lessons → narrated Manim animations. An LLM writes the `VoiceoverScene`, Manim
renders it, `manim-voiceover` synchronises TTS narration.

## How videos get made

Use the **`make-video` skill** (`.claude/skills/make-video/SKILL.md`). It owns the whole loop:
write the scene → `manim -ql` → repair errors → inspect rendered frames for layout problems →
promote to `-qh`.

There is no orchestration script, and that is deliberate. The previous pipeline
(`orchestrate.py`, `orchestrate.sh`, `extract_code.sh`, `extract_final.py`) shelled out to the
Gemini CLI and parsed Python back out of a JSON response. It never completed a run end to end —
its defects were all text-marshalling defects (cp1252 decoding of UTF-8 stdout, `shell=True`
quoting, the wrong JSON key, bare `return` on every failure path so it exited 0 when it failed).
Those files were deleted in favour of the skill, which has no marshalling layer to get wrong.
They remain in git history at `f44b789` if ever needed.

**Don't reintroduce a subprocess orchestrator** without revisiting D1 in the vault.

## Layout

| Path | |
|---|---|
| `context/*.md` | Source lessons. The pedagogical input |
| `generated/*.py` | Generated scenes. **Build artifacts — gitignored** |
| `media/` | Manim output: renders, TeX SVGs, TTS cache. **Gitignored** |
| `test_voiceover.py` | Toolchain smoke test |
| `.claude/skills/make-video/` | The generation + render loop |

## Conventions

- **Scene class names are chosen from the content**, in `PascalCase`, and stated to the user.
  Nothing defaults to a fixed name — a previous version assumed `GeneratedScene` while the
  model named its class `Chapter2Neuron`, so the render could never have been found.
- **Draft at `-ql`, ship at `-qh`.** A 1080p60 render with TTS costs minutes; never iterate there.
- **Narration is written to be spoken** — `"x one"`, not `"x_1"`.
- Full scene rules and known traps live in the skill, not here.

## Toolchain

Python 3.13 · Manim CE · `manim-voiceover` + gTTS (cloud; needs network at render time) ·
FFmpeg · MiKTeX/TeX Live.

Verify the environment with `manim -ql test_voiceover.py TestScene`. If that passes, a failure
is in the generated scene, not the setup.

## After a task that changes project state

Update the vault **and** its `System Map.canvas` — `Working Rules.md` there is the full rule.
Short form:

1. Update the notes the task touched (status, checklists, findings).
2. Update `System Map.md` + `System Map.canvas` — phase, next action, what is now verified.
3. Check `Home.md` still points at current reality.
4. A real render, or an interesting failure, gets a dated note in `Runs/`. Record the command
   **actually run**, not the one that was supposed to work.
5. New decision with more than one defensible answer → a new `D<n>` in `Open Decisions.md`,
   keeping the rejected options.
6. Never put API keys or secrets in the vault — `.env` only, and `.env` is gitignored here.

**"Works" means someone ran it and saw the output.** If a component is believed to work but has
not been run since it changed, the vault says *unverified*. Both repos are public-facing git
history; write accordingly.
