# manim-voiceover

Turn Markdown maths lessons into narrated [Manim](https://docs.manim.community/) animations.

An LLM writes the Manim scene from your prose, renders it, fixes what breaks, checks the
result, and produces an MP4 with synchronised narration and subtitles.

> **Status: prototype.** One lesson has been rendered end to end
> (`Chapter2Neuron` — the artificial neuron). The generation loop was rebuilt around Claude
> Code in September 2026 and has not yet been run across a batch of lessons. Expect to steer it.

## How it works

```
context/lesson.md
      │
      ▼
  [ Claude Code: write scene → manim -ql → read error → fix → inspect frames → manim -qh ]
      │
      ▼
media/videos/<scene>/1080p60/<Scene>.mp4  +  .srt
```

The repair loop is the point. Generated Manim code fails in four ways — syntax errors, runtime
errors, **layout errors** (overlapping labels, off-screen mobjects), and pedagogical errors.
The first two a script could catch. The third needs someone to look at a rendered frame, which
is why generation is a Claude Code skill rather than a pipeline script.

## Setup

**Python packages**

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**System dependencies** — all must be on `PATH`:

| | Why |
|---|---|
| [FFmpeg](https://ffmpeg.org/) | Muxing video and audio |
| [MiKTeX](https://miktex.org/) or TeX Live | `MathTex` compilation |
| [Claude Code](https://code.claude.com/docs/) | Runs the generation loop |

gTTS is cloud-based, so **rendering needs a network connection**.

`manim-voiceover` also ships `OpenAIService`, `ElevenLabsService`, `AzureService`, `CoquiService`,
`PyTTSX3Service` and `RecorderService` — swapping is one line in the scene. Only `OpenAIService`
works here without installing an extra. **There is no Piper service in the installed version**,
despite what older notes claimed. See `Skills/Skill Registry` in the vault.

## Verify the toolchain

```powershell
manim -ql test_voiceover.py TestScene
```

Exercises Manim, LaTeX, gTTS and FFmpeg together. Run this first whenever something breaks;
if it passes, the problem is in a generated scene rather than the setup.

## Make a video

Put a lesson in `context/`, open Claude Code in this directory, and ask:

```
make a video from context/your-lesson.md
```

The `make-video` skill takes it from there — writing the scene, rendering a draft, repairing
errors, checking the frames for layout problems, and promoting to 1080p60 once it's clean.
It'll tell you the scene class name and the output path.

To re-render or revise an existing scene, just say so — the generated `.py` stays in
`generated/` and the TTS cache means unchanged narration isn't re-synthesised.

## Repository layout

| Path | |
|---|---|
| `context/` | Source lessons (Markdown) — **your input** |
| `generated/` | Generated scenes — build artifacts, gitignored |
| `media/` | Renders, TeX SVGs, TTS cache — gitignored |
| `test_voiceover.py` | Toolchain smoke test |
| `.claude/skills/make-video/` | The generation and render loop |
| `CLAUDE.md` | Machine-facing project notes |

Project planning, decisions and run logs live in an Obsidian vault at
`personal-project-knowledge-vault/manim-voiceover`.
