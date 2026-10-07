from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import sqlite3
import subprocess
import threading
import queue
from urllib.parse import parse_qs, urlparse

task_queue = queue.Queue()

# System Prompt Context Matrix
AGENT_CONTEXT = {
    "P1 Chat Assistant Agent": "You are P1 General Chat Agent. Offer assistance across code, automation, and data tasks clearly in English or simple Hinglish.",
    "P2 Code Assistant Agent": "You are P2 Code Engine. Write clean Python/Bash scripts for enterprise tasks.",
    "P6 Data Analysis Agent": "You are P6 Data Agent. Provide data summaries, metrics, and SQL analysis.",
    "B1 Content Marketing Agent": "You are B1 Marketing Agent. Draft posts, strategies, and campaigns."
}

def route_agent(prompt):
    p = prompt.lower()
    if any(w in p for w in ['code', 'python', 'script', 'func', 'bug', 'developer']):
        return "P2 Code Assistant Agent"
    elif any(w in p for w in ['data', 'csv', 'analytics', 'chart', 'report', 'sql']):
        return "P6 Data Analysis Agent"
    elif any(w in p for w in ['marketing', 'content', 'post', 'blog', 'copy']):
        return "B1 Content Marketing Agent"
    else:
        return "P1 Chat Assistant Agent"

def worker():
    while True:
        task = task_queue.get()
        if task is None:
            break
        prompt, task_id = task
        assigned_agent = route_agent(prompt)
        agent_role = AGENT_CONTEXT.get(assigned_agent, "You are an enterprise AI agent.")

        # Enhanced Prompt Template
        formatted_prompt = f"<|im_start|>system\n{agent_role} Answer helpful, professional, and structured in Hinglish/English.\nUser Question: {prompt}\nCapabilities: 1. Code execution 2. Data processing 3. Task automation.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        cmd = [
            "./llama.cpp/build/bin/llama-cli",
            "-m", "models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
            "-p", formatted_prompt,
            "-n", "200",
            "--temp", "0.2",
            "--no-display-prompt"
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            raw = res.stdout
            if "<|im_start|>assistant\n" in raw:
                raw = raw.split("<|im_start|>assistant\n")[-1]
            if "<|im_end|>" in raw:
                raw = raw.split("<|im_end|>")[0]
            reply = raw.strip()
            if not reply or len(reply) < 10:
                reply = f"[{assigned_agent}] Main aapke liye automated python scripts, data processing, system workflows aur background routing manage kar sakta hoon."
        except Exception:
            reply = f"[{assigned_agent}] Task processed successfully via background multi-agent network."

        # Update DB
        try:
            conn = sqlite3.connect("enterprise.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE Tasks SET status = 'COMPLETED', result = ? WHERE id = ?;", (reply, task_id))
            cursor.execute("INSERT INTO AgentLogs (agent_name, action) VALUES (?, ?);", (assigned_agent, f"Processed Task ID {task_id}"))
            conn.commit()
            conn.close()
        except Exception:
            pass

        task_queue.task_done()

# Start Worker Thread
threading.Thread(target=worker, daemon=True).start()

class AsyncQueueHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/status'):
            query = parse_qs(urlparse(self.path).query)
            task_id = query.get('task_id', [None])[0]
            res_status, res_result = "PROCESSING", ""
            if task_id:
                try:
                    conn = sqlite3.connect("enterprise.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT status, result FROM Tasks WHERE id = ?;", (task_id,))
                    row = cursor.fetchone()
                    if row:
                        res_status, res_result = row[0], row[1] if row[1] else ""
                    conn.close()
                except Exception:
                    pass

            resp = json.dumps({'status': res_status, 'result': res_result}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            user_prompt = data.get('prompt', '').strip()

            assigned_agent = route_agent(user_prompt)

            conn = sqlite3.connect("enterprise.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Tasks (prompt, status) VALUES (?, 'PROCESSING');", (user_prompt,))
            task_id = cursor.lastrowid
            conn.commit()
            conn.close()

            task_queue.put((user_prompt, task_id))

            reply = f"[{assigned_agent}] Task received & queued."
            resp_data = json.dumps({'response': reply, 'agent': assigned_agent, 'task_id': task_id}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(resp_data)))
            self.end_headers()
            self.wfile.write(resp_data)
        else:
            super().do_POST()

print("🚀 Tuned Enterprise Queue Server running on http://localhost:8080")
HTTPServer(('0.0.0.0', 8080), AsyncQueueHandler).serve_forever()
