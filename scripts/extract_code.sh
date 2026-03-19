#!/bin/bash
# extract_code.sh
# Extracts Python code from a Gemini API JSON response

INPUT_JSON="$1"
OUTPUT_PY="$2"

if [ -z "$INPUT_JSON" ] || [ -z "$OUTPUT_PY" ]; then
  echo "Usage: ./extract_code.sh <input.json> <output.py>"
  exit 1
fi

if [ ! -f "$INPUT_JSON" ]; then
  echo "Error: File $INPUT_JSON not found."
  exit 1
fi

echo "Extracting raw response from $INPUT_JSON..."
# Use jq to get the raw string. In Gemini CLI headless output, it might be `.text` or just raw output if not strictly structured as nested.
# Let's assume standard gemini-cli output format when using --output-format json
RAW_MARKDOWN=$(jq -r '.text' "$INPUT_JSON")

# If .text is null, it might just be an array or different structure depending on CLI version. We fallback to . candidates if needed.
if [ "$RAW_MARKDOWN" == "null" ]; then
    RAW_MARKDOWN=$(jq -r '.' "$INPUT_JSON")
fi

echo "Filtering for Python code..."
# The awk script toggles a flag when it sees ```python and turns it off at the next ```
echo "$RAW_MARKDOWN" | awk '
/^```python/ {flag=1; next}
/^```/ {if(flag) {flag=0; next}}
flag {print}
' > "$OUTPUT_PY"

echo "Extraction complete. Python code saved to $OUTPUT_PY"
