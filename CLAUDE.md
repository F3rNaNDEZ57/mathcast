# CLAUDE.md — mathcast

Machine-facing notes for anyone — human or agent — working on the **plugin itself**.
If you just want to *use* mathcast, read `README.md` instead.

Machine-facing notes for this repo. The reasoning behind it lives in an Obsidian vault.

## The design constraints that matter

These are the decisions most likely to be undone by someone who doesn't know why they exist.
**Read this section before changing the architecture.**

| | |
|---|---|
| **Keep render → repair → inspect in one context** | It works because a single context holds the lesson, the scene, the traceback and the frames at once. Splitting it across sub-agents recreates the failure mode this project deleted an orchestrator to escape |
| **Don't reintroduce a subprocess orchestrator** | The previous pipeline shelled out to a CLI and parsed Python back out of JSON. Every one of its bugs was a text-marshalling bug. They were not fixed — they were deleted |
| **Nothing machine-specific ships** | `import ipv4_first` is conditional on `./ipv4_first.py` existing, which `/mathcast:init` writes only where it probed a black-holed IPv6 route |
| **A fix isn't shipped until the version bumps** | Plugin updates are version-gated. Bump `.claude-plugin/plugin.json`, then `claude plugin marketplace update` before `claude plugin update` |
| **Don't propose a third-party skill for TTS** | 404 were surveyed; none satisfies the `SpeechService` contract. Better narration is a one-line `self.set_speech_service(...)` swap |

> **Maintainer's note.** The full reasoning — numbered decisions, rejected options, and dated run
> logs — lives in a private Obsidian vault outside this repo. It is not needed to contribute; this
> file carries the constraints that actually bind. Where a rule below cites a `D<n>`, that is a
> pointer into those notes, not a file you're missing.

**Why the record matters here:** this repo has already shipped documentation that contradicted
its own code — a README describing a local-TTS `jq` pipeline that never existed. Whatever you
change, make the docs and the code agree in the same commit. Re-deriving a settled decision
wastes a turn; re-opening one without knowing why it was settled is worse.

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

The **`plan` skill** (`skills/plan/SKILL.md`) turns that outline into a scene split and beats.
It is where **D2** is answered — per lesson, not globally: default to one scene, split only for
length (>8 min), genuine independence, or risk isolation. There is no concatenation step, so a
split costs a manual join.

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
| `skills/plan/` | Outline → scene split + beats. **Decides D2 per lesson** |
| `skills/script/` | Plan → the exact spoken narration, word-counted |
| `skills/make-video/` | The render + repair + inspect loop |
| `assets/probe_env.py` | Toolchain + IPv6 + TTS probe. Bounded timeouts, never hangs |
| `assets/test_voiceover.py` | Toolchain smoke test |
| `assets/ipv4_first.py` | IPv6 shim **template**. Copied into a project only if the probe finds the fault |
| `inputs/` | Source material — md, pdf, links. **Gitignored — it is the user's** |
| `work/<lesson>/` | outline · plan · script · `mathcast.json`. **Gitignored** |
| `generated/*.py` | Generated scenes. **Build artifacts — gitignored** |
| `media/` | Manim output: renders, TeX SVGs, TTS cache. **Gitignored** |

## Conventions

- **Scene class names are chosen from the content**, in `PascalCase`, and stated to the user.
  Nothing defaults to a fixed name — a previous version assumed `GeneratedScene` while the
  model named its class `Chapter2Neuron`, so the render could never have been found.
- **Draft at `-ql`, ship at `-qh`.** A 1080p60 render with TTS costs minutes; never iterate there.
- **Narration is written to be spoken** — `"x one"`, not `"x_1"`. The `script` skill owns this.
- **Kokoro `af_sarah` speaks at ~177 words per minute** (measured over two scenes, 889 words).
  Scene length is `words / 177`, not a per-beat guess.
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

## After a change

**"Works" means someone ran it and saw the output.** If a component is believed to work but has
not been run since it changed, say *unverified* — in the README, in the PR, wherever the claim
appears. This repo's own status section is written that way on purpose.

Practically, for any change to the plugin:

1. `claude plugin validate .` must pass.
2. If you changed behaviour, **bump `version` in `.claude-plugin/plugin.json`** — otherwise the
   fix reaches nobody who has already installed.
3. Update the docs that the change touched, in the same commit.
4. Never commit API keys or secrets. `.env` is gitignored; `inputs/` is too, because the material
   people put there is theirs.

The maintainer additionally keeps dated run logs and numbered decisions in the private vault
mentioned above. That is not a contribution requirement.
