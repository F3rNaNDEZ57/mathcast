---
description: Set up a mathcast project here - probe the toolchain and network, scaffold the folders, pick a speech service
---

Set up the current directory as a mathcast project. Probe first, then scaffold, then report
honestly. **Do not assume anything is installed** — this may be a machine you have never seen.

## 1. Probe the environment

```bash
python "${CLAUDE_PLUGIN_ROOT}/assets/probe_env.py"
```

Read the JSON after the `---MATHCAST-JSON---` marker. It tells you three things:

| Field | What it decides |
|---|---|
| `toolchain.*` | Whether rendering can work at all |
| `network.ipv6_blackhole` | Whether scene rule 0 applies **on this machine** |
| `tts.*` | Which speech services can actually be constructed |

**If `manim`, `ffmpeg`, `latex` or `dvisvgm` is missing, stop and say so.** The plugin cannot
install them. Point at what is missing and let the user install it. A missing `dvisvgm` in
particular is easy to miss — LaTeX can be present and `MathTex` will still fail without it.

## 2. Scaffold the project

Create only what is missing; never overwrite an existing file.

```
inputs/      the learning material - .md, .pdf, .txt, or a links file
work/        outline.md, plan.md, <Scene>.script.md   (per lesson)
generated/   the Manim scenes you write
media/       Manim's output: renders, TeX, TTS cache
```

Append to `.gitignore` (create it if absent) — these are all build artifacts:

```
media/
generated/
work/
__pycache__/
*.onnx
voices-*.bin
```

## 3. Handle the network fault, if it is present

**Only if `network.ipv6_blackhole` is `true`:**

IPv6 is advertised on this network but unroutable, so every HTTPS request stalls ~21s in SYN
retries before falling back. gTTS makes ~4 requests per clip, so narration costs ~85s per clip
instead of ~0.6s. Copy the shim into the project and tell the user it is there and why:

```bash
cp "${CLAUDE_PLUGIN_ROOT}/assets/ipv4_first_template.py" ./ipv4_first.py
```

Scenes then need `import ipv4_first` as their first import (see the `make-video` skill, rule 0).

Also tell the user the real fix is one elevated command, and that it helps pip, npm and git too:

```
netsh interface ipv6 set prefixpolicy ::ffff:0:0/96 60 4
```

**Do not run it** — it needs an elevated prompt and is the user's decision. Undo is
`netsh interface ipv6 reset prefixpolicy`.

**If `ipv6_blackhole` is `false`, do none of this.** No shim, no rule 0, no mention.

## 4. Choose a speech service

Default to **gTTS** — it needs no install and no key. Then offer Kokoro, and let the probe
decide how hard to push it:

| Probe says | What to recommend |
|---|---|
| `ipv6_blackhole: true` or `online: false` | **Recommend Kokoro.** gTTS here is either broken or costs ~85s/clip |
| healthy network | Mention Kokoro as an optional upgrade — better voice, no network at render. Do not push |

If the user wants Kokoro, install it in **two steps**:

```bash
pip install kokoro-onnx soundfile
pip install kokoro-manim-voiceover --no-deps
```

> **Never run `pip install kokoro-manim-voiceover` on its own.** `manim-voiceover` pins
> `python-dotenv<0.22.0`, so a plain install downgrades `python-dotenv` — which breaks
> `fastmcp-slim` and `mcp` if the user has MCP tooling. `--no-deps` also avoids `manim-dsa`,
> a declared dependency the package never imports.

Kokoro needs model files (~338 MB). They are **not** per-project — put them in a shared cache
and pass the paths explicitly, because the package otherwise downloads them into the current
working directory:

```bash
mkdir -p ~/.cache/mathcast/kokoro
curl -4 -sSL -o ~/.cache/mathcast/kokoro/kokoro-v1.0.onnx \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -4 -sSL -o ~/.cache/mathcast/kokoro/voices-v1.0.bin \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

`curl -4` matters when the probe found the black-hole. Tell the user the size before starting.

Record the chosen service in `work/mathcast.json` so later stages don't re-ask:

```json
{"speech_service": "gtts", "ipv4_shim": false, "kokoro_models": null}
```

## 5. Verify the toolchain actually renders

Claims need evidence. Run the smoke test — it exercises Manim, LaTeX, the speech service and
FFmpeg together:

```bash
python -B -m manim -ql "${CLAUDE_PLUGIN_ROOT}/assets/test_voiceover.py" TestScene
```

**`-B` is not optional.** Without it Python writes `__pycache__` into the installed plugin
directory, which is shared, may be read-only, and can leave stale bytecode across a plugin
update. Verified 2026-09-18: a smoke-test run without `-B` dirtied
`<plugin>/assets/__pycache__`.

If it passes, the environment is good and any later failure is in the generated scene. If it
fails, the error is environmental — report it verbatim and stop.

## 6. Report

Tell the user, in this order:

1. What the probe found — toolchain versions, and the network verdict in one line.
2. What you created, and what you left alone because it already existed.
3. Which speech service is configured, and why that one.
4. Whether the smoke test passed, with the output path if it did.
5. What to do next: **put material in `inputs/`**, then ask for a video.

Do not claim anything works that you did not just watch work.
