# .github/scripts/ai_coder.py
import os
import sys
import json
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
    
    # Connect to the local Ollama service running on the runner
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama" # Required by the client but ignored by Ollama
    )
    
    system_prompt = (
        "You are an expert DevSecOps AI Engineer. Your job is to analyze security/linting errors "
        "and generate the exact replacement code or configuration to fix the issue.\n\n"
        "Rules:\n"
        "1. Fix SAST (Flake8, Bandit), Dockerfile (Hadolint), or Dependency (pip-audit) issues.\n"
        "2. Provide your output strictly in valid JSON format matching this schema:\n"
        '{"file_path": "relative/path/to/file", "new_content": "Full content of the file after your fix"}\n'
        "3. Output only the JSON. Do not include markdown code blocks like ```json."
        "4. CRITICAL: Never attempt to edit, modify, or output changes to any file ending in '.log'. "
        "Only fix the underlying source files (e.g., Python scripts, Dockerfiles, requirements.txt)."
    )
    
    user_prompt = f"The scanning pipeline failed with these logs:\n\n{error_context}\n\nInspect the error, fix the file, and return the JSON payload."
    
    try:
        response = client.chat.completions.create(
            model="qwen2.5-coder:7b", # Excellent model for syntax and structure processing
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1 # Low temperature ensures strict format adherence
        )
        
        raw_content = response.choices[0].message.content.strip()
        
        # Clean up code blocks if the model accidentally includes them
        if raw_content.startswith("```"):
            raw_content = raw_content.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            if raw_content.startswith("json"):
                raw_content = raw_content.split("\n", 1)[1].strip()

        result = json.loads(raw_content)
        file_to_fix = result.get("file_path")
        fixed_content = result.get("new_content")
        
        if file_to_fix and fixed_content:
            print(f"[AI AGENT] Applying local Ollama self-healing fix to: {file_to_fix}")
            with open(file_to_fix, 'w') as f:
                f.write(fixed_content)
        else:
            print("[AI AGENT] Local agent did not output a structured fix.")
            
    except Exception as e:
        print(f"[AI AGENT] Error processing agent request: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_agent()

