# GEMINI.md - Instructional Context for Manim-Voiceover Pipeline

## Project Overview
This project is an **Autonomous Generative Educational Animation Pipeline**. It integrates the Google Gemini CLI with Manim Community Edition and the `manim-voiceover` plugin to transform Markdown educational content into fully narrated, high-fidelity mathematical animations.

### Core Technologies
- **Gemini CLI**: Acts as the cognitive engine for zero-shot code generation.
- **Manim Community Edition**: The visual rendering engine for programmatic animation.
- **manim-voiceover**: A plugin that synchronizes animations with synthesized speech.
- **gTTS (Google Text-to-Speech)**: Currently used for acoustic synthesis (can be swapped for local models like Coqui or Piper if system dependencies allow).
- **Python 3.13**: The primary execution runtime.

### Architecture
1. **`context/`**: Contains raw Markdown files that serve as the pedagogical source material.
2. **`templates/`**: Contains `generation_prompt.md`, which defines the strict rules for the LLM's code generation.
3. **`scripts/`**: Contains orchestration logic. `orchestrate.py` is the primary entry point for Windows/Cross-platform execution.
4. **`generated/`**: Transient storage for LLM JSON responses and the extracted `chapter_scene.py` script.
5. **`media/`**: The standard Manim output directory for rendered video files and audio caches.

---

## Building and Running

### 1. Environment Setup
Install the necessary system dependencies:
- **Node.js** (for Gemini CLI)
- **FFmpeg** (for video multiplexing)
- **MiKTeX/TeX Live** (for MathTex rendering)

Install Python dependencies:
```powershell
pip install -r requirements.txt
pip install gTTS
```

### 2. Verify Baseline
Test the Manim + TTS synchronization with the provided test script:
```powershell
# Ensure your PATH includes Python scripts
$env:PATH = "C:\Users\owner\AppData\Roaming\Python\Python313\Scripts;" + $env:PATH
manim -qh test_voiceover.py TestScene
```

### 3. Run the Full Pipeline
Generate a video from a Markdown lesson:
```powershell
python scripts/orchestrate.py "context/YourLesson.md" --scene "YourSceneName"
```

---

## Development Conventions

### LLM Prompting Guidelines (`templates/generation_prompt.md`)
All generated Manim code must strictly adhere to these rules:
1. **Inheritance**: Must inherit from `VoiceoverScene`.
2. **Speech Service**: Initialize `GTTSService()` in the `construct` method.
3. **Synchronization**: Use `with self.voiceover(text="...") as tracker:` blocks.
4. **Math Rigor**: Use `MathTex` for all formulas and variables.
5. **Relative Positioning**: Use `.next_to()`, `.shift()`, and `.to_edge()` exclusively (no absolute coordinates).
6. **State Management**: Use `FadeOut` to clear the screen between conceptual parts to prevent visual clutter.

### Code Extraction
The pipeline uses a robust extraction logic in `scripts/orchestrate.py` that handles both structured JSON responses and raw Markdown, isolating code within ```python blocks.

### Troubleshooting
- **Path Issues**: Always ensure the Python Scripts folder and npm global bin are in the `env["PATH"]`.
- **Gemini CLI YOLO Mode**: The pipeline uses the `-y` flag to auto-approve tool calls (if any) during the inference phase.
- **Model Selection**: If `gemini-3.1-pro-preview` is unavailable, the orchestrator defaults to the most stable available model.
