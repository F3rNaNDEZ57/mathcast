#!/bin/bash
# orchestrate.sh
# Master pipeline execution script

CONTEXT_FILE="$1"
SCENE_NAME="${2:-GeneratedScene}"

if [ -z "$CONTEXT_FILE" ]; then
  echo "Usage: ./orchestrate.sh <path_to_context.md> [SceneName]"
  exit 1
fi

if [ ! -f "$CONTEXT_FILE" ]; then
  echo "Error: Context file $CONTEXT_FILE not found."
  exit 1
fi

PROMPT_TEMPLATE="templates/generation_prompt.md"
if [ ! -f "$PROMPT_TEMPLATE" ]; then
  echo "Error: Prompt template $PROMPT_TEMPLATE not found."
  exit 1
fi

JSON_OUT="generated/response.json"
PY_OUT="generated/chapter_scene.py"

echo "====================================================="
echo "Phase 1: Generative Inference via Gemini CLI"
echo "====================================================="
echo "Reading prompt template and context..."

# We use the @ operator native to gemini-cli to inject the context file.
# We also include the prompt template text.
# The command structure relies on reading the template and appending the @ reference.
PROMPT_CONTENT=$(cat "$PROMPT_TEMPLATE")
FULL_PROMPT="$PROMPT_CONTENT @$CONTEXT_FILE"

echo "Executing Gemini CLI in headless mode..."
# Using --json output format. Note: flags might differ slightly based on CLI version.
gemini -p "$FULL_PROMPT" --output-format json > "$JSON_OUT"

if [ $? -ne 0 ]; then
  echo "Error: Gemini CLI failed."
  exit 1
fi

echo "Inference complete. JSON payload saved to $JSON_OUT"

echo ""
echo "====================================================="
echo "Phase 2: Data Sanitation and Code Extraction"
echo "====================================================="
# We assume jq is available or execute it via WSL/GitBash
bash scripts/extract_code.sh "$JSON_OUT" "$PY_OUT"

if [ ! -s "$PY_OUT" ]; then
  echo "Error: Extraction failed or yielded empty file."
  exit 1
fi

echo ""
echo "====================================================="
echo "Phase 3: Visual and Acoustic Compilation via Manim"
echo "====================================================="
echo "Invoking Manim Community Edition with local TTS..."
# -qh for high quality 1080p60. 
# Depending on the system, we might want to pipe the output to the output folder.
manim -qh "$PY_OUT" "$SCENE_NAME"

if [ $? -eq 0 ]; then
  echo "Success! Pipeline finished."
  echo "Please check the media/videos directory for your generated MP4."
else
  echo "Manim compilation encountered an error. Please inspect $PY_OUT."
  exit 1
fi
