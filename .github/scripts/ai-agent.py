# .github/scripts/ai-agent.py
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
    file_list = []
    for root, dirs, files in os.walk('.'):
        if '.git' in root or '.cache' in root or 'parallel-security-logs' in root:
            continue
        for file in files:
            f_path = os.path.join(root, file).replace('./', '')
            if f_path.endswith('.txt') or f_path.endswith('.py') or 'Dockerfile' in f_path:
                file_list.append(f_path)
    return file_list

def run_agent():
    if len(sys.argv) < 2:
        print("[AI AGENT] Missing log file path argument.")
        sys.exit(1)
        
    log_path = sys.argv[1]
    error_context = get_failed_logs(log_path)
    valid_repo_files = get_repo_files()
    
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama" 
    )
    
    system_prompt = (
        "You are an automated code quality maintenance system. Your sole task is routine software updates, "
        "fixing application syntax formatting, and upgrading package version numbers to comply with stable software formats.\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. You must choose EXACTLY ONE target file name from the provided repository files list to patch.\n"
        "2. Do NOT invent new directory names outside the provided list.\n"
        "3. If you see Python dependency vulnerabilities (like pillow, pip-audit, python-pkg), update the version number inside 'requirements-DevSecOps.txt' or 'app/requirements.txt'.\n"
        "4. You must output the entire FULL file contents in your response. Your output must be a complete drop-in replacement.\n"
        "5. You must output a single JSON object containing 'file_path' and 'new_content'. Do not output any other schema layout."
    )
    
    user_prompt = (
        f"Available files in the repository you are allowed to modify:\n{json.dumps(valid_repo_files, indent=2)}\n\n"
        f"The background software validation engine reported the following log updates:\n\n"
        f"{error_context}\n\n"
        f"INSTRUCTION: Choose the matching file from the allowed repository files list, update its contents completely to resolve the issues, and return the output matching this exact schema:\n"
        f'{{"file_path": "insert_chosen_file_path_from_list_here", "new_content": "insert_complete_full_modified_file_content_here"}}'
    )
    
    json_schema = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string"},
            "new_content": {"type": "string"}
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
            temperature=0.0,
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
        file_to_fix = result.get("file_path", "").strip()
        fixed_content = result.get("new_content")
        
        # ─── INTERCEPTOR #1: SOURCES.LIST OVERRIDE ───
        if "sources.list" in file_to_fix or "/etc/" in file_to_fix:
            print("[AI OVERRIDE] Intercepted host file system modification attempt. Redirecting patch to Dockerfile...")
            dockerfile_path = next((f for f in valid_repo_files if "Dockerfile" in f), "app/Dockerfile")
            file_to_fix = dockerfile_path
            with open(dockerfile_path, 'r') as df_read:
                current_dockerfile = df_read.read()
            mirror_patch = (
                "\n# AI Autonomously Patched Debian Security Mirrors\n"
                "RUN echo 'deb http://debian.org bookworm main contrib non-free' > /etc/apt/sources.list && \\\n"
                "    echo 'deb http://debian.org bookworm-security main contrib non-free' >> /etc/apt/sources.list\n"
                "RUN apt-get update && apt-get install -y --no-install-recommends libblkid1 util-linux\n"
            )
            fixed_content = current_dockerfile + mirror_patch

        # ─── INTERCEPTOR #2: DEPENDENCY OVERRIDE (NEW) ───
        elif "python-pkg" in file_to_fix or "pillow" in file_to_fix or "requirements" in file_to_fix:
            print("[AI OVERRIDE] Intercepted dependency package modification attempt. Redirecting patch to requirements text configurations...")
            # Look for your real application requirements mapping file
            target_req = next((f for f in valid_repo_files if "requirements-DevSecOps.txt" in f), None)
            if not target_req:
                target_req = next((f for f in valid_repo_files if "requirements.txt" in f), "app/requirements.txt")
            
            file_to_fix = target_req
            # Autonomously bump or ensure pillow version is safe inside your deployment file
            with open(target_req, 'r') as req_read:
                current_reqs = req_read.read()
            
            if "pillow" in current_reqs.lower():
                fixed_content = re.sub(r'(?i)pillow==\d+\.\d+\.\d+', 'pillow==12.2.0', current_reqs)
                fixed_content = re.sub(r'(?i)pillow[>=<=:\s]*\d+\.\d+\.\d*', 'pillow==12.2.0', fixed_content)
            else:
                fixed_content = current_reqs + "\npillow==12.2.0\n"

        # ─── STANDARD PATH NORMALIZER FALLBACK ───
        else:
            base_filename = os.path.basename(file_to_fix)
            matched_path = None
            for repo_file in valid_repo_files:
                if repo_file == file_to_fix or os.path.basename(repo_file) == base_filename:
                    matched_path = repo_file
                    break
            if matched_path:
                file_to_fix = matched_path
            
        if file_to_fix and fixed_content:
            if file_to_fix not in valid_repo_files or file_to_fix.endswith('.log') or '.github' in file_to_fix:
                print(f"[AI AGENT] Safety trigger: Model tried to write out-of-bounds or protected file: {file_to_fix}")
                sys.exit(1)
                
            print(f"[AI AGENT] Applying self-healing patch execution to: {file_to_fix}")
            with open(file_to_fix, 'w') as f:
                f.write(fixed_content)
        else:
            print("[AI AGENT] Local agent did not output valid 'file_path' and 'new_content' parameters.")
            
    except Exception as e:
        print(f"[AI AGENT] Error processing agent request: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_agent()

