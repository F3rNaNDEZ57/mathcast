import os
import sys
import json
import subprocess
import argparse

def extract_code(json_file, py_file):
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found.")
        return False
    
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    if not content:
        print("Error: Gemini response is empty.")
        return False

    try:
        data = json.loads(content)
        # gemini-cli --output-format json puts the response in a field, usually 'text' or just the whole thing
        if isinstance(data, dict) and 'text' in data:
            raw_markdown = data['text']
        elif isinstance(data, dict) and 'response' in data:
             raw_markdown = data['response']
        else:
            raw_markdown = str(data)
    except json.JSONDecodeError:
        # If it's not valid JSON, treat it as raw markdown
        raw_markdown = content

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
    
    if not code_lines:
        print("Error: No Python code block found in Gemini response.")
        # Debug: print the first 100 chars of raw_markdown
        print(f"Raw response start: {raw_markdown[:100]}...")
        return False
    
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(code_lines))
    
    print(f"Extraction complete. Code saved to {py_file}")
    return True

def run_pipeline(context_file, scene_name="GeneratedScene"):
    prompt_template = "templates/generation_prompt.md"
    if not os.path.exists(prompt_template):
        print(f"Error: {prompt_template} not found.")
        return
    
    with open(prompt_template, 'r', encoding='utf-8') as f:
        prompt_content = f.read()
    
    # Construct command for gemini-cli
    # gemini-cli supports @file syntax
    cmd = ["gemini", "-y", "-p", f"{prompt_content} @{context_file}", "--output-format", "json"]
    
    print("=====================================================")
    print("Phase 1: Generative Inference via Gemini CLI")
    print("=====================================================")
    
    # Add npm global bin to path
    npm_path = os.path.expandvars(r'%APPDATA%\npm')
    env = os.environ.copy()
    env["PATH"] = npm_path + os.pathsep + env["PATH"]

    json_out = "generated/response.json"
    try:
        # Join command for shell
        full_cmd = subprocess.list2cmdline(cmd)
        print(f"Running command: {full_cmd}")
        result = subprocess.run(full_cmd, capture_output=True, text=True, check=True, shell=True, env=env)
        print("Subprocess stdout length:", len(result.stdout))
        print("Subprocess stderr:", result.stderr)
        with open(json_out, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
        print(f"Inference complete. JSON payload saved to {json_out}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing Gemini CLI: {e.stderr}")
        return

    print("\n=====================================================")
    print("Phase 2: Data Sanitation and Code Extraction")
    print("=====================================================")
    py_out = "generated/chapter_scene.py"
    if not extract_code(json_out, py_out):
        return

    print("\n=====================================================")
    print("Phase 3: Visual and Acoustic Compilation via Manim")
    print("=====================================================")
    manim_cmd = ["manim", "-qh", py_out, scene_name]
    try:
        subprocess.run(manim_cmd, check=True)
        print("Success! Pipeline finished.")
    except subprocess.CalledProcessError as e:
        print(f"Error compiling Manim scene: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Manim Pipeline Orchestrator")
    parser.add_argument("context", help="Path to context markdown file")
    parser.add_argument("--scene", default="GeneratedScene", help="Manim Scene class name")
    args = parser.parse_args()
    
    run_pipeline(args.context, args.scene)
