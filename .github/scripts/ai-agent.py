# .github/scripts/ai_coder.py
import os
import sys
import json
import re
from openai import OpenAI

def get_failed_logs(log_file_path):
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as f:
            return f.read()
    return "No log file found."

def get_repo_files():
    # Scan the workspace directory so the AI agent knows exactly what files exist
    file_list = []
    for root, dirs, files in os.walk('.'):
        # Skip hidden git and cache folders
        if '.git' in root or '.cache' in root or 'parallel-security-logs' in root:
            continue
        for file in files:
            file_list.append(os.path.join(root, file).replace('./', ''))
    return file_list

def run_agent():
    if len(sys.argv) < 2:
        print("[AI AGENT] Missing log file path argument.")
        sys.exit(1)
        
    log_path = sys.argv[1]
    error_context = get_failed_logs(log_path)
    
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama" 
    )
    
    system_prompt = (
        "You are an automated code quality maintenance system. Your sole task is routine software updates, "
        "fixing syntax formatting, and incrementing package versions to comply with the latest standard software updates.\n\n"
        "Rules:\n"
        "1. Read the provided compilation, style, or dependency log entries.\n"
        "2. Identify which source file or config file requires a version upgrade or formatting rewrite.\n"
        "3. Provide your output strictly in valid JSON format matching this schema:\n"
        '{"file_path": "relative/path/to/file", "new_content": "Full content of the file after your updates"}\n'
        "4. DO NOT provide comments, introductions, or explanations. Only emit the JSON schema parameters.\n"
        "5. CRITICAL: Never attempt to edit, modify, or output changes to any file ending in '.log'."
    )
    
    user_prompt = (
        f"Available files in the repository:\n{json.dumps(get_repo_files, indent=2)}\n\n"
        f"The background software validation engine reported the following log updates:\n\n"
        f"{error_context}\n\n"
        f"INSTRUCTION: Choose the broken file from the repository files list, update its contents to fix the issues listed in the log, and return the output matching this exact schema:\n"
        f'{{"file_path": "insert_chosen_file_path_here", "new_content": "insert_complete_modified_file_content_here"}}'
    )

    # Define a strict JSON schema for Ollama to follow
    json_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The relative path to the source file or configuration being patched (e.g. app/Dockerfile or requirements.txt)"
            },
            "new_content": {
                "type": "string",
                "description": "The exact full replacement text content of the target file with the security fixes fully implemented."
            }
        },
        "required": ["file_path", "new_content"]
    }
    
    try:
        response = client.chat.completions.create(
            model="qwen2.5-coder:7b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            # FORCE OLLAMA TO FOLLOW SCHEMA
            response_format={
                "type": "json_object",
                "schema": json_schema
            }
        )
        
        raw_content = response.choices[0].message.content.strip()
        print(f"[AI DEBUG] Raw Model Output:\n{raw_content}\n")
        
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if json_match:
            clean_json = json_match.group(0)
        else:
            clean_json = raw_content

        result = json.loads(clean_json)
        file_to_fix = result.get("file_path")
        fixed_content = result.get("new_content")
        
        if file_to_fix and fixed_content:
            # Prevent the model from hallucinating or modifying system log/workflow files
            if file_to_fix not in repo_files or file_to_fix.endswith('.log') or '.github' in file_to_fix:
                print(f"[AI AGENT] Safety trigger: Model tried to write out-of-bounds file: {file_to_fix}")
                sys.exit(1)
                
            print(f"[AI AGENT] Applying local Ollama self-healing fix to: {file_to_fix}")
            with open(file_to_fix, 'w') as f:
                f.write(fixed_content)
        else:
            print("[AI AGENT] Local agent did not output valid 'file_path' and 'new_content' parameters.")
            
    except Exception as e:
        print(f"[AI AGENT] Error processing agent request: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_agent()

