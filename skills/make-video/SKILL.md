---
name: make-video
description: Turn a lesson into a narrated Manim animation. Use when the user asks to make, generate, render, or re-render a video, animation, or explainer from a lesson/chapter/note in inputs/ or work/, or names a Manim scene to build or fix. Handles the whole loop - write the scene, render, repair errors, check layout, promote to final quality.
---

# Make a narrated Manim video from a Markdown lesson

Turn prose in `inputs/` (or a `work/<lesson>/*.script.md` written by an earlier stage) into a rendered, narrated animation. You write the scene, render
it, fix what breaks, look at the result, and only then pay for a final-quality render.

## The loop

Never render at `-qh` first. A 1080p60 render with TTS takes minutes; `-ql` takes seconds.

```
read lesson  →  write scene  →  manim -ql  ─┬─ error?  → read stderr, fix, re-render
                                            └─ ok?     → inspect frames → fix layout → manim -qh
```

### 1. Read the lesson

Prefer the most-processed artifact that exists. In order:

| If this exists | Use it |
|---|---|
| `work/<lesson>/<Scene>.script.md` | The narration and beats are already chosen. Don't re-derive them |
| `work/<lesson>/plan.md` | **The usual case today.** Scene split, beats, timings and risks are chosen. Build exactly the parts it lists - if it records something as *omitted*, leave it out rather than helpfully restoring it |
| `work/<lesson>/outline.md` | Concepts, maths and notation extracted and reviewed, but no scene plan yet. Run the `plan` skill first, or plan inline if the lesson is obviously one scene. Read its *Flagged for review* section either way |
| only `inputs/` | No outline yet. **Run the `ingest` skill first** - don't animate straight from raw material, because nobody has checked the extraction |

If the user named a file, use it. If `inputs/` is empty and there is no `work/`, say so and stop.

Decide the **scene class name** yourself from the content — `PascalCase`, descriptive
(`GradientDescent`, `Chapter2Neuron`). Write it to `generated/<snake_case_name>.py`. Tell the
user both names; everything downstream needs them.

### 2. Write the scene

Follow **Scene rules** below. Write the complete file in one pass — don't stub it.

### 3. Render at draft quality

```bash
manim -ql generated/<file>.py <SceneName>
```

On failure, read the actual error and fix the cause:

| Error | Usual cause |
|---|---|
| `LaTeX ... undefined control sequence` | A macro that needs a package, or a typo. Check `media/Tex/*.log` for the real TeX error — the Python traceback truncates it |
| `AttributeError` on a mobject | Method doesn't exist in Manim CE (often a `manimgl` idiom) |
| `TypeError: unexpected keyword` | Wrong kwarg for that class |
| Hangs on first voiceover | gTTS needs network. **If each clip takes ~85s, `import ipv4_first` is missing** - see rule 0 |

Retry up to **3 times**. If it still fails, stop and show the user the error and the code —
don't keep grinding.

### 4. Look at the output

This is the step a script cannot do, and the reason this is a skill.

```bash
ls media/videos/<file>/480p15/<SceneName>.mp4
```

Extract frames and **actually Read them** — one per voiceover block is plenty. Write them
under `media/` (already gitignored) rather than a temp dir; this is Windows and path
translation is where this project has historically broken:

```bash
mkdir -p media/frames/<SceneName>
ffmpeg -i media/videos/<file>/480p15/<SceneName>.mp4 \
  -vf fps=1/4 -y media/frames/<SceneName>/frame_%03d.png
```

Check each frame for:

- **Overlap** — text or mobjects sitting on top of each other
- **Off-screen** — anything past the frame edge (Manim's frame is 14.22 × 8 units)
- **Occlusion** — a new mobject covering one still being referenced
- **Leftovers** — something that should have been cleared by a `FadeOut` and wasn't
- **Crowding** — more than ~3 mobject groups on screen at once

Fix what you find and re-render at `-ql`. These defects render without error — nothing but
looking will catch them.

### 5. Promote to final quality

Only once the draft is clean:

```bash
manim -qh generated/<file>.py <SceneName>
```

Report the output path, the duration, and anything you changed and why.

## Scene rules

Non-negotiable — generated code must obey all of these.

0. **`import ipv4_first` as the first import - but only if `./ipv4_first.py` exists.**
   `/mathcast:init` writes that file only on machines where it probed an IPv6 black-hole
   (IPv6 advertised but unroutable, so every HTTPS request stalls ~21s in SYN retries
   before falling back). gTTS makes ~4 requests per clip, so on an affected machine a
   narration clip costs ~85s instead of ~0.6s - measured 2026-09-17.
   **If the file is not there, the machine does not have the fault. Do not add the import.**
   It is also irrelevant when the speech service is Kokoro, which never touches the network.
1. **Inherit from `VoiceoverScene`** (`from manim_voiceover import VoiceoverScene`).
2. **Set the speech service first** in `construct()`. Use whatever `work/mathcast.json`
   records - `/mathcast:init` wrote it. Default:
   `self.set_speech_service(GTTSService())`
   (`from manim_voiceover.services.gtts import GTTSService`)

   For `"speech_service": "kokoro"`, pass the cached model paths explicitly - the package
   otherwise downloads 338 MB into the working directory:
   ```python
   from kokoro_mv import KokoroService
   self.set_speech_service(KokoroService(
       voice="af_sarah", lang="en-us",
       model_path=..., voices_path=...))   # paths from work/mathcast.json
   ```
   Kokoro costs ~1.4s/clip and needs no network. It returns no word boundaries; add
   `transcription_model="base"` to any service if a scene uses `wait_until_bookmark()`.
3. **Every animation lives in a voiceover block:**
   ```python
   with self.voiceover(text="...") as tracker:
       self.play(Write(eq), run_time=tracker.duration)
   ```
   Use `tracker.duration` as `run_time`. To split one block across several animations, divide
   it — `tracker.duration * 0.3`, `tracker.duration * 0.7` — so the sum is the whole duration.
4. **`MathTex` for all maths** — every equation, formula, and single variable. `Text` is for
   plain-English labels only. Never put a variable in a `Text`.
5. **Relative positioning only** — `.next_to()`, `.shift()`, `.to_edge()`, `.arrange()`.
   No absolute coordinate arrays. Position against what's already on screen.
6. **Clear between concepts** — `self.play(FadeOut(*self.mobjects))` between major parts.
   Keeping the screen clean is what makes it readable.
7. **Narration is spoken, not read.** Write `"x one"`, not `"x_1"`; `"two thirds"`, not
   `"2/3"`; `"approximately"`, not `"≈"`. TTS reads the string literally.

### Traps

- **`set_color_by_tex` matches substrings.** `set_color_by_tex("b", YELLOW)` also colours
  `\mathbf{...}` via the `b` in `mathbf`. Use `set_color_by_tex_to_color_map`, or index the
  `MathTex` parts directly.
- **`FadeOut(*self.mobjects)` needs mobjects.** Calling it on an empty scene raises. Only use
  it after something has been added.
- **A mobject created inside a `with` block is still in scope after it** — but only if that
  block ran. Don't reference a mobject from a branch that may not have executed.
- **Narration length drives pacing.** A 3-second line cannot carry a 10-second animation.
  Match the text to the visual work.

## Output layout

| Path | |
|---|---|
| `inputs/` | The source material |
| `work/<lesson>/` | outline, plan, script, `mathcast.json` |
| `generated/<file>.py` | The scene you write |
| `media/videos/<file>/480p15/` | Draft renders (`-ql`) |
| `media/videos/<file>/1080p60/` | Final render (`-qh`) + `.srt` + `.wav` |
| `media/voiceovers/` | Cached TTS, keyed by text hash — unchanged narration isn't re-synthesised |

`media/` is gitignored. Don't commit renders.

## Check the toolchain first if something looks environmental

```bash
python -m manim -ql "${CLAUDE_PLUGIN_ROOT}/assets/test_voiceover.py" TestScene
```

That exercises Manim, LaTeX, gTTS, and FFmpeg together. If it passes, the problem is in the
generated scene, not the setup.
