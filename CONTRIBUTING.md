# Contributing to mathcast

Thanks for looking. Issues, questions and pull requests are all welcome.

If you just want to *use* mathcast, [README.md](README.md) is the place. This file is for
changing it.

---

## Before you change anything

Three rules carry most of the weight here. They exist because breaking them has already cost
this project time.

### 1. The render → repair → inspect loop stays in one context

`make-video` works because a single context holds the lesson, the scene, the traceback and the
rendered frames at the same time. The repair loop reads an error from code it just wrote; frame
inspection compares what it sees against what it intended.

Splitting that across sub-agents looks like a tidy refactor and breaks the only part of this
project that has been proven end to end. Don't.

### 2. A fix isn't shipped until the version bumps

Plugin updates are **version-gated**. Merging a fix delivers nothing to anyone who already
installed until `version` in `.claude-plugin/plugin.json` changes.

We learned this the hard way: a bug fix was merged, `claude plugin update` reported *"already at
the latest version"*, and the installed copy kept the bug. Bump the version in the same PR.

### 3. "Works" means someone ran it

If you changed something and haven't run it, say so — in the PR, in the README, wherever the
claim appears. The README's [Status](README.md#status) section is deliberately split into
*proven* and *not yet exercised*, and that honesty is load-bearing: this repo once shipped a
README describing a pipeline that never existed.

Unverified work is welcome. Unverified work described as working is not.

---

## Setting up

```bash
git clone https://github.com/F3rNaNDEZ57/mathcast
cd mathcast
claude plugin marketplace add .
claude plugin install mathcast@mathcast
```

Restart Claude Code. See [Requirements](README.md#requirements) for FFmpeg, LaTeX and the Python
packages — `python assets/probe_env.py` tells you what's missing.

Iterating on plugin files? Remember rule 2: bump the version, then
`claude plugin marketplace update mathcast && claude plugin update mathcast`.

---

## Before you open a PR

```bash
claude plugin validate .
```

Then check:

- [ ] Version bumped in `.claude-plugin/plugin.json` if behaviour changed
- [ ] Docs updated **in the same commit** as the code they describe
- [ ] Anything you didn't run is described as unverified
- [ ] No secrets. `.env` is gitignored, and so is `inputs/` — material people put there is theirs

---

## Good places to start

The honest gaps, taken straight from the README's status section. Each is genuinely useful and
none requires deep knowledge of the internals:

| | What's needed |
|---|---|
| **`init` on macOS** | The `brew` path is written but has never run — mathcast was developed on Windows |
| **`init` on Linux** | Same for the `sudo` hand-off. It should *print* the command, never run it — confirm it does |
| **A PDF over 10 pages** | `ingest` pages through long PDFs in chunks of 20. Every test input so far has been 3 pages |
| **Link ingestion** | Written, never exercised. Give it a file of URLs and see what happens |
| **A seamless split** | When a lesson splits across scenes, the join works but visibly resets — scene B rebuilds what scene A ended on. Needs the plan stage to hand off visual state, or own the cut |
| **A LaTeX compile error** | The repair loop has handled imports and two Manim API errors, never a TeX failure |

A bug report for any of these is as useful as a fix.

---

## Reporting a bug

Please include the output of:

```bash
python assets/probe_env.py
```

It reports your toolchain versions, which package managers you have, whether your network has
the IPv6 fault, and which speech services can be constructed — which is most of what anyone
would ask you anyway. It makes no network requests beyond a bounded connection test and prints
no credentials.

---

## Where to ask

- **[Discussions](https://github.com/F3rNaNDEZ57/mathcast/discussions)** — questions, ideas,
  showing what you made
- **[Issues](https://github.com/F3rNaNDEZ57/mathcast/issues)** — bugs and concrete proposals

---

## Licence

By contributing you agree your contributions are licensed under [Apache-2.0](LICENSE), the same
as the project.
