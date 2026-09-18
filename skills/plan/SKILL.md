---
name: plan
description: Turn a reviewed outline into a scene plan - how many scenes, what each covers, the beats and their rough timings. Use after ingest, when work/<lesson>/outline.md exists and the user wants to proceed toward a video, or when asked to plan/structure/storyboard a lesson. Writes work/<lesson>/plan.md.
---

# Plan the scenes for a lesson

Turn `work/<lesson>/outline.md` into `work/<lesson>/plan.md` — how the lesson becomes one or
more Manim scenes, what each covers, and the beats inside them.

**This is an artifact, not a gate.** Write it and keep going. The outline was the place a human
stopped; this file exists so the decision is inspectable and re-runnable, not so it can be
approved.

## Before anything

Read `work/<lesson>/outline.md`, **including its *Flagged for review* section.**

If something there is marked blocked, inferred, or missing:

- **Blocked** (a formula the source never gives) — you cannot plan a beat around it. Either the
  user has since supplied it, or **leave that concept out of the plan and say so at the top**.
  Do not quietly invent the missing piece.
- **Inferred** — plan it, but carry the flag into `plan.md` so it stays visible downstream.

If there is no outline, run the `ingest` skill first. Do not plan from raw `inputs/`.

## 1. Decide the scene split

**Default: one scene per lesson.** Split only for a reason you can state.

This is **D2**, decided per lesson rather than globally, because the evidence cuts both ways:
draft renders are cheap (56s for 41 animations, 20 narration clips), which removes most of the
pain splitting would solve — but a failure in part 5 still wastes parts 1-4.

Split when **any** of these holds:

| Reason | Threshold |
|---|---|
| Length | Estimated final video over ~8 minutes |
| Independence | Parts share no mobjects and no visual continuity — a cut between them costs nothing |
| Risk isolation | One part is materially riskier (3D, graphs, heavy `Transform` chains) and shouldn't be able to waste the rest |

Do **not** split merely because the outline has numbered concepts. `ArtificialNeuron` ran five
parts, 20 voiceover blocks and 41 animations as a single scene at 2:42, and that was fine.

> **If you do split, say so loudly.** There is no concatenation step in this project yet, so
> multiple scenes means multiple MP4s and a manual join. That cost is real — record it at the
> top of `plan.md` so nobody discovers it after rendering.

## 2. Name the scenes

`PascalCase`, derived from content: `ArtificialNeuron`, `GradientDescent`, `ChainRule`. One
file per scene, `generated/<snake_case>.py`.

State every name you chose. Everything downstream — the render command, the output path — needs
them, and a name nobody was told is a scene nobody can find.

## 3. Write the plan

`work/<lesson>/plan.md`:

```markdown
---
lesson: artificial-neuron
scenes:
  - class: ArtificialNeuron
    file: generated/artificial_neuron.py
    covers: [1, 2, 3, 5]
    estimated: 6 min
split: single
omitted: [4]          # blocked in the outline - see below
---

# Plan — artificial neuron

**Omitted:** concept 4 (perceptron update rule). The outline flags it as having no formula
in the source. Not planned; not invented.

**Split:** one scene. Estimated 6 min, under the 8-minute threshold, and parts 2, 3 and 5
share the equation `z` on screen - cutting between them would break continuity.

## ArtificialNeuron

### Part 1 — biological to artificial  (~60s, outline §1)
| Beat | Narration gist | Visual | Animation |
|---|---|---|---|
| 1.1 | the four correspondences | `VGroup` of paired `Text` rows | `Write`, staggered |
| 1.2 | the diagram | circle + 3 input arrows + weight labels | `Create` circle, then `GrowArrow` |

**Clear after:** yes - nothing from part 1 is referenced later.

### Part 2 — the induced local field  (~75s, outline §2)
...
```

For each beat record: **what is said** (gist, not final wording — that is the script stage),
**what is on screen**, and **which animation** puts it there.

### Rules

1. **Every beat traces to an outline concept.** Cite the section. A beat with no source is an
   invention — if you need connective tissue, mark it.
2. **Respect the scene rules.** `MathTex` for all maths, relative positioning only, clear
   between parts. They live in the `make-video` skill; the plan must not propose something
   that violates them.
3. **Budget the time from word count, not from beat count.** Narration drives pacing —
   roughly 150 words per minute, and Kokoro runs slightly faster than that.

   > **Measured 2026-09-18:** a plan budgeted at 5m 30s for 5 parts rendered at **2m 16s** —
   > a 2.4x overestimate. Per-beat guesses compound badly. Write the narration gist first,
   > count the words, divide by 150. If a scene's beats total under ~750 words it is not a
   > five-minute scene, whatever the beat count suggests.

   This matters for the split decision: an inflated estimate will split a lesson that did not
   need splitting, and the split costs a manual join.
4. **Keep worked examples whole.** Their steps are the best animation material in any lesson;
   never collapse one into its result.
5. **Say what gets cleared.** Screen state between parts is where layout defects come from.
6. **Name the risks.** Crowding, long `Transform` chains, anything with more than ~3 mobject
   groups on screen at once. The frame-inspection step will look for exactly these.

## 4. Report

Say: the scenes and their names, the split decision and why, anything omitted because the
outline blocked it, and the risks you flagged. Then continue — `make-video` can work from
`plan.md`, or the script stage can if it exists.

## Traps

- **Planning around a blocked concept.** The outline flags things for a reason. Inventing the
  missing formula is the single worst failure available here, because it renders cleanly and
  is wrong.
- **Splitting by default.** Concatenation doesn't exist. One scene unless you can state why not.
  Check the word-count budget before invoking the length threshold - beat-count intuition
  overestimated by 2.4x the one time it was measured.
- **Over-specifying narration.** Gist only. Exact wording is the script stage's job, and
  narration written here tends to read like prose rather than speech.
- **Forgetting `\|` in outline tables.** Outlines contain LaTeX; a raw `|` inside a Markdown
  table cell breaks it.
