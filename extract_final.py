import json
import os

json_file = r'C:\Projects\manim-voiceover\generated\response.json'
py_file = r'C:\Projects\manim-voiceover\generated\chapter_scene.py'

# Try utf-16 first, fallback to utf-8
try:
    with open(json_file, 'r', encoding='utf-16') as f:
        data = json.load(f)
except (UnicodeDecodeError, json.JSONDecodeError):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

raw_markdown = data['response']
lines = raw_markdown.split('\n')
code_lines = []
in_block = False
for line in lines:
    if line.strip().startswith('```python'):
        in_block = True
        continue
    elif line.strip().startswith('```') and in_block:
        in_block = False
        break
    if in_block:
        code_lines.append(line)

with open(py_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(code_lines))

print(f"Extracted code to {py_file}")
