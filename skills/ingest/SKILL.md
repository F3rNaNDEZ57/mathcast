---
name: ingest
description: Read learning material in inputs/ - PDFs, Markdown, text, or links - and extract it into a reviewable outline. Use when the user adds material to inputs/, asks to ingest/extract/summarise a source, asks what a document contains, or asks for a video from material that has no outline yet. Produces work/<lesson>/outline.md and stops for review.
---

# Extract learning material into an outline

Turn whatever is in `inputs/` into `work/<lesson>/outline.md` — a structured, reviewable
account of what the material actually teaches.

**This is the one stage that stops for a human.** Everything downstream (scene planning,
narration, rendering) runs from the outline, so an error here propagates into a video that
costs minutes to render. Getting the outline wrong is cheap to fix; getting it wrong *silently*
is not.

## The contract

```
inputs/*.{pdf,md,txt}  +  links  →  work/<lesson-slug>/outline.md  →  STOP, ask for review
```

One outline per **lesson**, not per file. A 40-page PDF is usually several lessons; three short
notes on one topic are usually one.

## 1. Find the material

List `inputs/`. If the user named a file, use it. If `inputs/` is empty, say so and stop —
don't go hunting elsewhere.

| Kind | How to read it |
|---|---|
| `.md`, `.txt` | Read directly |
| `.pdf` | Read with the `pages` parameter. **Required above 10 pages**, and never more than 20 pages per call — page through it |
| Links | A `.md`/`.txt` of URLs, or URLs the user pastes. Fetch each one |
| Images, scans | Read them. If a PDF is a scan with no text layer, say so — it needs OCR, which is not set up |

**If the material is large** — a long PDF, many files, or several links — delegate the reading
to a subagent and ask it for the outline content only. Large input, small output is the one
shape where a separate context helps. Keep the *writing* of the file in your own context so you
can check it against what the user asked for.

## 2. Decide the lesson boundaries

Read enough to see the structure before splitting anything.

A lesson is **one thing a person could learn in a single sitting** — typically 3-8 minutes of
finished video. Split on conceptual boundaries, not page counts. A worked example belongs with
the concept it demonstrates.

Name each lesson in `kebab-case` from its content (`gradient-descent`, `artificial-neuron`).
That name becomes the directory, and later the `PascalCase` scene class.

**Tell the user the split and why, before writing anything.** If the material is obviously one
lesson, don't ceremonially ask.

## 3. Write the outline

`work/<lesson-slug>/outline.md`, one per lesson:

```markdown
---
lesson: gradient-descent
sources:
  - inputs/optimisation-notes.pdf (pp. 14-22)
estimated_video: 5-7 min
status: awaiting-review
---

# Gradient descent

## What this teaches
One paragraph. The thing a viewer should be able to do afterwards.

## Prerequisites
What the material assumes the viewer already knows. Say "none stated" if the source
doesn't say - don't invent a prerequisite chain.

## Concepts, in teaching order

### 1. The cost surface
- **Claim:** ... what the source actually asserts
- **Maths:** `J(\theta) = \frac{1}{2m}\sum(h_\theta(x_i) - y_i)^2`
- **Visual:** a bowl-shaped surface with a point descending it
- **Source:** p. 15

### 2. ...

## Worked examples
Any example the source works through, with its numbers. These make the best animation
beats - keep them.

## Notation to verbalise
Narration is spoken, so record how each symbol should be *said*:
| Symbol | Spoken as |
|---|---|
| `\theta_j` | "theta j" |
| `\alpha` | "the learning rate alpha" |

## Flagged for review
- Anything ambiguous, contradictory, or missing in the source
- Anything you inferred rather than read
- Anything that will be hard to animate and may need rethinking
```

### Rules for the content

1. **Extract, don't invent.** Everything traceable to the source. If you add connective
   material, put it under *Flagged for review* and say so.
2. **Keep the maths exact.** Copy formulas precisely, in LaTeX. A transcription error here
   becomes a wrong equation on screen.
3. **Record where each concept came from** — page, section or heading. The plan stage needs it,
   and a reviewer needs to check you.
4. **Note what is visual.** The `Visual:` line is a hint for the plan stage, not a commitment.
   Material with nothing to show is material that makes a bad video — say so.
5. **Flag honestly.** An empty *Flagged for review* section on a 40-page source means you
   didn't look hard enough.

## 4. Stop

Report: the lessons found, where each outline is, and **what you flagged**. Then stop and ask
the user to read the outline before anything else runs.

Do not plan scenes. Do not write narration. Do not render. The gate exists because it's the one
cheap place to catch a misreading.

## Traps

- **A PDF over 10 pages fails without `pages`.** Page through in chunks of 20 or fewer.
- **Slides are not prose.** A deck's bullet fragments need expanding into claims — that
  expansion is inference, so flag it.
- **Don't collapse worked examples into their result.** The steps are the animation.
- **A source's own recommendations can be wrong.** This project's source document recommends
  `set_color_by_tex("b", YELLOW)`, which mis-colours `\mathbf`. Record what the source says,
  but the scene rules in the `make-video` skill win.
- **`work/` is gitignored.** Outlines are working state, not source. Don't add them to git.
