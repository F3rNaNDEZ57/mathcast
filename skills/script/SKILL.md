---
name: script
description: Turn a scene plan into the actual spoken narration, beat by beat, with a word-counted duration. Use after plan, when work/<lesson>/plan.md exists and the user wants to proceed toward a video, or when asked to write/revise the narration or script for a lesson. Writes work/<lesson>/<Scene>.script.md.
---

# Write the narration

Turn `work/<lesson>/plan.md` into one `work/<lesson>/<Scene>.script.md` per scene — the exact
words that will be spoken, attached to the beat that plays while they are said.

**An artifact, not a gate.** Write it and keep going. `ingest` was the place a human stopped.
This file exists so narration can be read, edited and re-rendered without regenerating anything
else — and because narration is the one part of a video a person can fix without knowing Manim.

## Why this stage earns its place

Two reasons, both concrete:

1. **It is the only honest duration estimate.** The plan *guesses* per-beat timings, and on the
   one occasion that was measured it was **2.4x too high** — 5m30s budgeted, 2m16s rendered.
   A script can be counted.

   > **Measured 2026-09-18, two scenes, same voice:**
   > | Scene | Words | Rendered | Implied |
   > |---|---|---|---|
   > | `GaussianAnatomy` | 402 | 135.9s | **177.5 wpm** |
   > | `GaussianGeometry` | 487 | 164.8s | **177.3 wpm** |
   >
   > Agreement to 0.2 wpm across two independent scenes. **Use `words ÷ 177` for Kokoro
   > `af_sarah` at speed 1.0.** The familiar 150 wpm is a human-presenter figure and
   > overestimates by 18%.
   >
   > A different voice, a different `speed=`, or a different service needs its own constant —
   > render one scene, count its words, divide. It takes one render to measure and removes the
   > guess permanently.

2. **Narration drives every `run_time` in the scene.** `tracker.duration` comes from the audio,
   so the words decide the pacing. Writing them last, inside the Python, is how you end up with
   a three-second sentence carrying a ten-second animation.

## 1. Read the plan

Read `work/<lesson>/plan.md` in full, including anything marked **omitted** or carried forward
as **inferred** from the outline.

- **Omitted** — write no narration for it. Do not reintroduce a concept the outline blocked.
- **Inferred** — write it, and keep the flag in the script's front matter so it stays visible.

If there is no plan, run the `plan` skill first. If there is no outline either, run `ingest`.

## 2. Write for the ear

This is the whole craft of the stage. The text is **spoken by a TTS engine that reads literally**
and never asks what you meant.

| Write | Not |
|---|---|
| "x one" | `x_1` |
| "two thirds" | `2/3` |
| "approximately" | `≈` |
| "eighty one point eight five percent" | `81.85%` |
| "mu, the mean" | `μ` |
| "sigma squared" | `σ²` |
| "the cumulative distribution function" | "the CDF" (first mention) |
| "for example" | "e.g." |
| "nought point nine nine three eight" | `0.9938` |

Further rules:

- **Short sentences.** A TTS engine takes its breath at punctuation. A forty-word sentence
  with no comma comes out as an airless rush.
- **Say the symbol, then its meaning** — "mu, the mean" — the first time it appears. After that
  the bare name is fine.
- **No parentheticals or asides.** They do not survive speech; the listener cannot see brackets.
- **Never reference the screen with "here" or "this".** Say what the thing *is*. The viewer may
  be listening while looking away, and "as you can see here" is dead air if they are not.
- **Read it aloud in your head.** If you stumble, so will the engine.

## 3. Write the file

`work/<lesson>/<Scene>.script.md`:

```markdown
---
lesson: gaussian-distribution
scene: GaussianGeometry
plan: work/gaussian-distribution/plan.md
words: 487
estimated: 2m 45s        # words / 177 (measured, see above)
inferred: []             # carried forward from the outline
---

# Script — GaussianGeometry

## B1 — the empirical rule

### B1.1  (38 words · ~13s)
> Here is the standard normal again. What makes it so useful in practice is that
> the area under it is carved up in a way worth memorising.

**Visual:** `Create` axes, then `Create` curve.

### B1.2  (24 words · ~8s)
> Mark the axis out in standard deviations from the mean. One sigma, two sigma,
> three sigma, on each side.

**Visual:** `Write` the mu label, then `LaggedStart` the six tick labels.
```

Rules for the file:

1. **The blockquote is the exact string** that goes into `self.voiceover(text=...)`. Not a
   summary of it. If it is not ready to be spoken verbatim, it is not finished.
2. **Count the words per beat** and give the implied seconds at 177 wpm — about 3 words a
   second. It keeps the arithmetic visible and stops a beat quietly ballooning.
3. **Total in the front matter.** `words / 177` is the scene's real length. If it disagrees with
   the plan by more than about 30%, **say so in your report** — and if the plan split the lesson
   on a length argument that the word count no longer supports, say that too.
4. **One file per scene.** The scene class name is in the filename and the front matter.
5. **Match the beat IDs to the plan.** `B1.2` here is `B1.2` there. Someone editing narration
   should not have to guess which animation it belongs to.

## 4. Check the pacing against the visual

For each beat, ask whether the words can carry the animation:

- A beat whose visual is a four-part `Transform` chain needs a sentence long enough to cover it.
- A beat whose visual is one `FadeIn` does not want three sentences.
- `tracker.duration * 0.4` style splits only work if the narration has a natural seam there.

Where they do not match, **change the words, not the animation** — the plan chose the visuals
deliberately and they trace back to the outline. If a visual genuinely cannot be narrated,
that is a finding to report, not to paper over.

## 5. Report

Say: the files written, the **word-counted duration per scene**, how that compares to the plan's
estimate, and anything you had to flag. Then continue — `make-video` builds from the script.

## Traps

- **Writing prose.** Narration that reads well on a page often sounds stilted aloud. Sentences
  can be shorter and plainer than writing instinct wants.
- **Reintroducing an omitted concept** because the gap in the flow is uncomfortable. The gap is
  the point; the outline blocked it for a reason.
- **Numbers read as digits.** Kokoro and gTTS both handle plain integers well, but decimals,
  percentages and subscripts need spelling out.
- **Trusting the plan's timing.** It is a guess. Yours is a count. When they disagree, the count
  is right — and it may mean the scene split was unnecessary.
- **Losing the source.** Every claim still traces to the outline. Rewriting for the ear is a
  change of register, not licence to add content.
