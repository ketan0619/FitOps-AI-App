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
        "You are an expert DevSecOps AI Engineer. Your job is to analyze security/linting errors "
        "and generate the exact replacement code or configuration to fix the issue.\n\n"
        "Rules:\n"
        "1. Fix SAST (Flake8, Bandit), Dockerfile (Hadolint), or Dependency (pip-audit) issues.\n"
        "2. Provide your output strictly in valid JSON format matching this schema:\n"
        '{"file_path": "relative/path/to/file", "new_content": "Full content of the file after your fix"}\n'
        "3. CRITICAL: Never attempt to edit, modify, or output changes to any file ending in '.log'."
    )
    
    user_prompt = f"The scanning pipeline failed with these logs:\n\n{error_context}\n\nInspect the error, fix the file, and return the JSON payload."
    
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
            print(f"[AI AGENT] Applying local Ollama self-healing fix to: {file_to_fix}")
            if os.path.dirname(file_to_fix):
                os.makedirs(os.path.dirname(file_to_fix), exist_ok=True)
            with open(file_to_fix, 'w') as f:
                f.write(fixed_content)
        else:
            print("[AI AGENT] Local agent did not output valid 'file_path' and 'new_content' parameters.")
            
    except Exception as e:
        print(f"[AI AGENT] Error processing agent request: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_agent()

