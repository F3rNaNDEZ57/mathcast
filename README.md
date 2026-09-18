# mathcast

Turn maths and science learning material into narrated [Manim](https://docs.manim.community/)
animations — a Claude Code plugin.

Claude writes the Manim scene from your material, renders it, fixes what breaks, looks at the
result, and produces an MP4 with synchronised narration and subtitles.

> **Status: early.** The render loop is proven — a 2:42 narrated animation was generated,
> repaired and shipped end to end on 2026-09-17. The plugin packaging around it landed
> 2026-09-18 and is newer than that: `/mathcast:init` is written and its environment probe is
> verified, but the command itself has not been exercised end to end. The **ingest stage is
> built and has been run** on real material; its PDF and link paths are not yet exercised.
> The **plan stage is built** and exercised. The scripting stage doesn't exist, so `make-video`
> reads `plan.md` directly for now.
> Expect to steer it.

## How it works

```
inputs/                        your material - md, pdf, links
   │
   ├─[ ingest ]──→ work/<lesson>/outline.md        ◀ the one review gate   ✅ built
   ├─[ plan ]────→ work/<lesson>/plan.md            scene split, beats   ✅ built
   ├─[ script ]──→ <Scene>.script.md                (not built yet)
   │
   └─[ write scene → manim -ql → read error → fix → inspect frames → manim -qh ]   ◀ proven
                         │
                         ▼
        media/videos/<scene>/1080p60/<Scene>.mp4  +  .srt
```

The repair loop is the point. Generated Manim code fails in four ways — syntax errors, runtime
errors, **layout errors** (overlapping labels, off-screen mobjects), and pedagogical errors. The
first two a script could catch. The third needs someone to look at a rendered frame, which is why
this is a Claude Code skill rather than a pipeline script. On the first real run, frame
inspection caught two defects that rendered without any error at all.

That last box stays in **one context** deliberately — it works because a single context holds the
lesson, the scene, the traceback and the frames at the same time.

## Install

```bash
/plugin marketplace add F3rNaNDEZ57/mathcast
/plugin install mathcast
```

For local development, point the marketplace at a clone instead:
`/plugin marketplace add /path/to/mathcast`.

## Set up a project

```
/mathcast:init
```

This probes rather than assumes. It reports your toolchain, checks whether IPv6 is advertised but
unroutable on your network (a fault that makes cloud TTS ~140× slower), scaffolds `inputs/` and
`work/`, picks a speech service, and runs a smoke test that exercises Manim, LaTeX, TTS and
FFmpeg together.

**System dependencies** — all must be on `PATH`; the plugin cannot install them:

| | Why |
|---|---|
| [FFmpeg](https://ffmpeg.org/) | Muxing video and audio |
| [MiKTeX](https://miktex.org/) or TeX Live | `MathTex` compilation — **including `dvisvgm`** |
| Python 3.11+ with `manim` and `manim-voiceover` | The renderer |

## Narration

**gTTS** is the default: nothing to install, no API key, but it calls Google **at render time**,
so rendering needs a network connection.

**Kokoro** is the offline option and `/mathcast:init` will offer it — Kokoro-82M, Apache-2.0,
~1.4s per clip, no key and no network once the model is cached. Install it in **two steps**:

```bash
pip install kokoro-onnx soundfile
pip install kokoro-manim-voiceover --no-deps
```

> Do **not** run `pip install kokoro-manim-voiceover` on its own. `manim-voiceover` pins
> `python-dotenv<0.22.0`, so a plain install downgrades `python-dotenv` and breaks `fastmcp-slim`
> and `mcp` if you use MCP tooling. `--no-deps` also avoids `manim-dsa`, a declared dependency the
> package never imports.

It needs ~338 MB of model files; keep them in a shared cache and pass the paths explicitly, or
the package downloads them into your current working directory.

`manim-voiceover` also ships `OpenAIService`, `ElevenLabsService`, `AzureService`, `CoquiService`,
`PyTTSX3Service` and `RecorderService`. Swapping is one line in the scene — but each needs its own
optional extra installed first; only `OpenAIService` works out of the box. **There is no Piper
service**, despite what older notes claimed.

Word-level timing (`wait_until_bookmark()`) does not depend on the service — pass
`transcription_model="base"` to any of them and `manim-voiceover` runs Whisper over the audio.

## Make a video

Put material in `inputs/` — Markdown, PDFs, text, or a file of links — then:

```
ingest inputs/
```

That extracts everything into `work/<lesson>/outline.md` and **stops**, so you can check what
it actually understood before anything expensive runs. Read the outline, especially its
*Flagged for review* section, then:

```
make a video from work/artificial-neuron/outline.md
```

The `make-video` skill takes it from there — writing the scene, rendering a draft, repairing
errors, checking frames for layout problems, and promoting to 1080p60 once clean. It tells you
the scene class name and the output path.

To re-render or revise, just say so. The generated `.py` stays in `generated/`, and the TTS cache
means unchanged narration isn't re-synthesised.

## Repository layout

| Path | |
|---|---|
| `.claude-plugin/` | `plugin.json` and `marketplace.json` |
| `commands/init.md` | `/mathcast:init` |
| `skills/ingest/` | Material → `work/<lesson>/outline.md`, the review gate |
| `skills/plan/` | Outline → `work/<lesson>/plan.md`: scene split, beats, risks |
| `skills/make-video/` | The render, repair and inspect loop |
| `assets/probe_env.py` | Toolchain, network and TTS probe — bounded timeouts, never hangs |
| `assets/test_voiceover.py` | Toolchain smoke test |
| `assets/ipv4_first_template.py` | IPv6 shim template, copied into a project only if the probe finds the fault |
| `inputs/` | Your material |
| `work/`, `generated/`, `media/` | Build artifacts — gitignored |
| `CLAUDE.md` | Machine-facing project notes |

Planning, decisions and run logs live in an Obsidian vault at
`personal-project-knowledge-vault/manim-voiceover`.
