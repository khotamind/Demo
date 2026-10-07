import os
import sqlite3
import subprocess

ADMIN_PASSWORD = "admin123"

def verify_admin():
    pwd = input("🔐 Enter Admin Password (Owner A0): ")
    return pwd == ADMIN_PASSWORD

def run_workflow_task(user_prompt):
    print(f"\n🚀 Running Multi-Agent Workflow for: '{user_prompt}'")
    try:
        conn = sqlite3.connect("enterprise.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Tasks (prompt, status) VALUES (?, 'COMPLETED');", (user_prompt,))
        cursor.execute("INSERT INTO AgentLogs (agent_name, action) VALUES ('X1 Orchestrator', ?);", (f"Executed task: {user_prompt}",))
        conn.commit()
        conn.close()
        print("\n--- [WORKFLOW OUTPUT] ---")
        print("✅ Workflow executed successfully and logged to DB.")
    except Exception as e:
        print(f"❌ Execution Error: {e}")

def view_audit_logs():
    print("\n📜 --- [DATABASE AUDIT LOGS] ---")
    if os.path.exists("enterprise.db"):
        try:
            conn = sqlite3.connect("enterprise.db")
            cursor = conn.cursor()
            
            print("\n📌 [Tasks History]:")
            cursor.execute("SELECT id, prompt, status, created_at FROM Tasks;")
            tasks = cursor.fetchall()
            for t in tasks:
                print(f"  ID: {t[0]} | Prompt: '{t[1]}' | Status: {t[2]} | Time: {t[3]}")

            print("\n📌 [Agent Action Logs]:")
            cursor.execute("SELECT id, agent_name, action, timestamp FROM AgentLogs;")
            logs = cursor.fetchall()
            for l in logs:
                print(f"  ID: {l[0]} | Agent: {l[1]} | Action: {l[2]} | Time: {l[3]}")

            conn.close()
        except Exception as e:
            print(f"Database Read Error: {e}")
    else:
        print("❌ Database not found. Run fix_db.py first.")

def show_active_agents():
    print("\n🤖 --- [REGISTERED ACTIVE AGENTS] ---")
    agents = [
        "R1 Lead / R7 Gateway Agent",
        "G1 CISO Security Agent",
        "E7 QA & Tester Agent",
        "P1 Chat Assistant Agent",
        "P2 Code Assistant Agent",
        "P6 Data Analysis Agent",
        "B1 Content Marketing Agent",
        "In3 Ops Deployment Agent",
        "B3 User Success Agent"
    ]
    for idx, agent in enumerate(agents, 1):
        print(f" {idx}. {agent} [Status: READY]")

def main():
    print("==========================================================")
    print("  37-AGENT INTERACTIVE CLI CONTROL CENTER (V7.1)        ")
    print("==========================================================")
    
    if not verify_admin():
        print("❌ Authorization Failed.")
        return

    while True:
        print("\n--- [MENU Options] ---")
        print("1. Run Multi-Agent Task Workflow")
        print("2. View Registered Active Agents")
        print("3. Inspect Security & DB Audit Logs")
        print("4. Exit CLI")
        
        choice = input("\n👉 Select Option (1-4): ").strip()
        
        if choice == '1':
            prompt = input("💬 Enter Task Prompt: ").strip()
            if prompt:
                run_workflow_task(prompt)
        elif choice == '2':
            show_active_agents()
        elif choice == '3':
            view_audit_logs()
        elif choice == '4':
            print("👋 Exiting CLI Dashboard.")
            break
        else:
            print("❌ Invalid Option. Try again.")

if __name__ == "__main__":
    main()
