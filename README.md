# Autonomous Generative Educational Animation Pipeline

This repository contains an end-to-end pipeline designed to autonomously synthesize mathematical animations using the Gemini CLI, Manim Community Edition, and localized Text-to-Speech (TTS) models.

## Repository Architecture
- **`context/`**: Place your raw markdown educational texts here.
- **`templates/`**: Contains the zero-shot prompting strategies (`generation_prompt.md`).
- **`scripts/`**: Holds the bash orchestrator (`orchestrate.sh`) and jq extraction utility (`extract_code.sh`).
- **`generated/`**: The transient build folder where the JSON payload and sanitized python scripts are deposited.
- **`media/`**: Manim's native output directory. Compiled MP4s are located here.

## 1. System Requirements

### Python Environment
Requires Python 3.9+ due to underlying PyTorch dependencies.
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### System Dependencies
You must have the following installed and accessible in your system's PATH:
- **Node.js**: Required to run the Gemini CLI (`npm install -g @google/gemini-cli`).
- **FFmpeg**: Required by Manim for multiplexing video and audio streams.
- **SoX**: Required by `manim-voiceover` for temporal manipulation.
- **TeX Live / MiKTeX**: Required for `MathTex` compilation.
- **jq**: Required by `scripts/extract_code.sh` for JSON processing.

## 2. Phase 2 Verification (Local TTS Test)
Before invoking the full generative pipeline, verify your Manim configuration, Coqui PyTorch bindings, and LaTeX engine by running the test script:

```bash
manim -qh test_voiceover.py TestScene
```
*If successful, an MP4 will be generated and played, demonstrating text, equations, and synchronized localized audio.*

## 3. Orchestrating the Generative Pipeline
To execute the pipeline against a markdown document:

```bash
bash scripts/orchestrate.sh context/Automating_Manim_Video_Creation.md
```

### Workflow Execution Log:
1. **The Cognitive Engine**: The script dynamically injects the context file into the prompt template and invokes the `gemini` CLI in headless mode. The JSON response is routed to `generated/response.json`.
2. **The Sanitation Layer**: `scripts/extract_code.sh` utilizes `jq` and `awk` to filter the markdown artifacts and extract the raw executable python to `generated/chapter_scene.py`.
3. **The Visual Rendering Engine**: The script spins up Manim, which dynamically evaluates the generated AST, connects to the local Coqui/Piper acoustic models for synthesis, and executes spatial interpolation via FFmpeg.
