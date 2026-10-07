import re
import subprocess
import os

ADMIN_PASSWORD = "admin123"

def verify_admin():
    pwd = input("🔐 Enter Admin Password (Owner A0): ")
    return pwd == ADMIN_PASSWORD

def run_llama_direct(system_instruction, user_prompt):
    formatted_prompt = f"<|im_start|>system\n{system_instruction}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"
    
    cmd = [
        "./llama.cpp/build/bin/llama-cli",
        "-m", "models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
        "-p", formatted_prompt,
        "-n", "1500",
        "--temp", "0.1",
        "--no-display-prompt"
    ]
    
    res = subprocess.run(cmd, input="", capture_output=True, text=True)
    raw = res.stdout

    if "<|im_start|>assistant\n" in raw:
        raw = raw.split("<|im_start|>assistant\n")[-1]
    if "<|im_end|>" in raw:
        raw = raw.split("<|im_end|>")[0]
    return raw.strip()

def security_audit_pass(user_prompt):
    print("\n🛡️ [G1 Security & Safety Agent (CISO)] Conducting Audit...")
    sec_prompt = (
        "You are G1 CISO Security Agent. Evaluate if request is malicious (e.g. hack, malware, exploit, steal credentials). "
        "Creating workflow execution engine and secure audit logging pipeline is SAFE. "
        "Reply strictly with PASS or REJECT."
    )
    result = run_llama_direct(sec_prompt, user_prompt).upper()
    if "REJECT" in result and "PASS" not in result:
        print("⛔ [SECURITY VETO TRIGGERED]: Task flagged as unsafe.")
        return False
    print("✅ [Security Audit Passed]: Approved.")
    return True

def build_workflow_pipeline(prompt):
    print("\n⚙️ [X1 Orchestrator & G1 Audit] Building Multi-Agent Workflow Engine...")
    
    wf_sys_prompt = (
        "You are X1 Orchestrator Agent. Write a Python script (workflow_engine.py) that loads "
        "router.py, main.py, product_agents.py, data_content_agents.py, and growth_ops_agents.py "
        "to execute a chained multi-agent workflow with audit logging into database. "
        "Output pure Python code inside ```python ``` block."
    )
    raw_output = run_llama_direct(wf_sys_prompt, prompt)
    
    match = re.search(r"```python\s*(.*?)\s*```", raw_output, re.DOTALL | re.IGNORECASE)
    py_code = match.group(1) if match else raw_output
    
    with open("workflow_engine.py", "w") as f:
        f.write(py_code.strip())
        
    print("✅ Success: 'workflow_engine.py' (Multi-Agent Workflow Engine) created successfully.")

def orchestrator_x1(user_prompt):
    print(f"\n👔 [X1 Orchestrator (SGM)] Initializing 37-Agent Management Pipeline...")
    
    if not security_audit_pass(user_prompt):
        return

    build_workflow_pipeline(user_prompt)

def main():
    print("==========================================================")
    print("  37-AGENT WORKFLOW & AUDIT ENGINE (V6.0)                ")
    print("==========================================================")
    
    if not verify_admin():
        print("❌ Authorization Failed.")
        return

    req = input("\n💬 Enter Project Goal / Requirement (Owner A0): ").strip()
    if req:
        orchestrator_x1(req)

if __name__ == "__main__":
    main()
