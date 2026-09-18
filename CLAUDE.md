# CLAUDE.md — mathcast

> **Renamed 2026-09-18** (D6.1). This repo is becoming the **`mathcast`** Claude Code plugin.
> The GitHub remote is still `F3rNaNDEZ57/manim_voiceover` until the user renames it.

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

Use the **`make-video` skill** (`skills/make-video/SKILL.md`). It owns the render half of the
loop: write the scene → `manim -ql` → repair errors → inspect rendered frames for layout
problems → promote to `-qh`.

**That loop must stay in one context** (D5). It works because a single context holds the lesson,
the scene, the traceback and the frames at once. Splitting it across subagents recreates D1's
failure mode under a new name.

`/mathcast:init` (`commands/init.md`) sets a project up: probes the toolchain and network,
scaffolds the folders, and picks a speech service.

The **`ingest` skill** (`skills/ingest/SKILL.md`) is the stage above it: material in `inputs/`
→ `work/<lesson>/outline.md`, then **stop for review**. It is the one human gate in D5, and it
exists because a misreading is cheap to fix in an outline and expensive after a render.

There is no orchestration script, and that is deliberate. The previous pipeline
(`orchestrate.py`, `orchestrate.sh`, `extract_code.sh`, `extract_final.py`) shelled out to the
Gemini CLI and parsed Python back out of a JSON response. It never completed a run end to end —
its defects were all text-marshalling defects (cp1252 decoding of UTF-8 stdout, `shell=True`
quoting, the wrong JSON key, bare `return` on every failure path so it exited 0 when it failed).
Those files were deleted in favour of the skill, which has no marshalling layer to get wrong.
They remain in git history at `f44b789` if ever needed.

**Don't reintroduce a subprocess orchestrator** without revisiting D1 in the vault.

## Layout

Plugin assets are tracked; everything a *project* produces is gitignored.

| Path | |
|---|---|
| `.claude-plugin/` | `plugin.json` + `marketplace.json` |
| `commands/init.md` | `/mathcast:init` — probe, scaffold, choose a speech service |
| `skills/ingest/` | Material → outline. The review gate |
| `skills/make-video/` | The render + repair + inspect loop |
| `assets/probe_env.py` | Toolchain + IPv6 + TTS probe. Bounded timeouts, never hangs |
| `assets/test_voiceover.py` | Toolchain smoke test |
| `assets/ipv4_first.py` | IPv6 shim **template**. Copied into a project only if the probe finds the fault |
| `inputs/` | Source material — md, pdf, links. *(was `context/`)* |
| `work/<lesson>/` | outline · plan · script · `mathcast.json`. **Gitignored** |
| `generated/*.py` | Generated scenes. **Build artifacts — gitignored** |
| `media/` | Manim output: renders, TeX SVGs, TTS cache. **Gitignored** |

## Conventions

- **Scene class names are chosen from the content**, in `PascalCase`, and stated to the user.
  Nothing defaults to a fixed name — a previous version assumed `GeneratedScene` while the
  model named its class `Chapter2Neuron`, so the render could never have been found.
- **Draft at `-ql`, ship at `-qh`.** A 1080p60 render with TTS costs minutes; never iterate there.
- **Narration is written to be spoken** — `"x one"`, not `"x_1"`.
- **Nothing machine-specific ships.** `import ipv4_first` is conditional on `./ipv4_first.py`
  existing, which `/mathcast:init` writes only where it probed the fault (D6.2).
- Full scene rules and known traps live in the skill, not here.

## Toolchain

Python 3.13 · Manim CE · `manim-voiceover` + gTTS (cloud; needs network at render time) ·
FFmpeg · MiKTeX/TeX Live.

Verify the environment with `python assets/probe_env.py`, then
`python -m manim -ql assets/test_voiceover.py TestScene`. If those pass, a failure is in the
generated scene, not the setup.

**Local TTS works** (D6.5): `kokoro-manim-voiceover` gives ~1.4s/clip with no network.
Install it in **two steps** — `pip install kokoro-onnx soundfile` then
`pip install kokoro-manim-voiceover --no-deps`. **Never the bare one-liner**: `manim-voiceover`
pins `python-dotenv<0.22.0`, so it downgrades `python-dotenv` and breaks `fastmcp-slim`/`mcp`.

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
