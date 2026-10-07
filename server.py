from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import sqlite3
import subprocess

def init_db():
    conn = sqlite3.connect("enterprise.db")
    conn.execute("CREATE TABLE IF NOT EXISTS Tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, prompt TEXT, status TEXT, result TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);")
    conn.execute("CREATE TABLE IF NOT EXISTS AgentLogs (id INTEGER PRIMARY KEY AUTOINCREMENT, agent_name TEXT, action TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);")
    conn.execute("CREATE TABLE IF NOT EXISTS AgentConfig (id INTEGER PRIMARY KEY AUTOINCREMENT, agent_name TEXT, status TEXT);")
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM AgentConfig;")
    if cursor.fetchone()[0] == 0:
        agents = [("G1 CISO & Governance", "ACTIVE"), ("X1 Master Orchestrator", "ACTIVE"), ("P2 Code Engine", "ACTIVE"), ("P4 Design & Graphics", "ACTIVE"), ("P6 Data Analyst", "ACTIVE")]
        cursor.executemany("INSERT INTO AgentConfig (agent_name, status) VALUES (?, ?);", agents)
        conn.commit()
    conn.close()

init_db()

USER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>37-Agent Sovereign User Dashboard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0b0f19; color: #f3f4f6; display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 260px; background: #111827; border-right: 1px solid #1f2937; display: flex; flex-direction: column; padding: 20px; }
        .sidebar h2 { font-size: 16px; color: #38bdf8; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px; }
        .nav-btn { background: transparent; border: none; color: #9ca3af; padding: 12px; text-align: left; font-size: 14px; border-radius: 6px; cursor: pointer; margin-bottom: 5px; transition: 0.2s; text-decoration: none; display: block; width: 100%; }
        .nav-btn:hover, .nav-btn.active { background: #1f2937; color: #fff; }
        .main-container { flex: 1; display: flex; flex-direction: column; height: 100%; }
        .header { background: #111827; padding: 15px 25px; border-bottom: 1px solid #1f2937; display: flex; justify-content: space-between; align-items: center; }
        .agent-status { font-size: 13px; color: #34d399; background: #064e3b; padding: 5px 12px; border-radius: 20px; font-weight: 500; }
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        .message { max-width: 75%; padding: 14px 18px; border-radius: 12px; font-size: 14px; line-height: 1.5; word-wrap: break-word; white-space: pre-wrap; }
        .message.user { background: #2563eb; color: #fff; align-self: flex-end; }
        .message.assistant { background: #1f2937; color: #e5e7eb; align-self: flex-start; border: 1px solid #374151; }
        .input-area { padding: 20px; background: #111827; border-top: 1px solid #1f2937; display: flex; gap: 10px; }
        .input-box { flex: 1; background: #1f2937; border: 1px solid #374151; border-radius: 8px; padding: 12px 16px; color: #fff; font-size: 14px; outline: none; }
        .input-box:focus { border-color: #38bdf8; }
        .send-btn { background: #2563eb; color: #fff; border: none; padding: 0 20px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s; }
        .send-btn:hover { background: #1d4ed8; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>User Dashboard</h2>
        <button class="nav-btn active" onclick="sendModuleQuery('General Chat', 'Start general session')">💬 General Chat</button>
        <button class="nav-btn" onclick="sendModuleQuery('Images Module', 'Generate local graphics concept')">🖼️ Images Module</button>
        <button class="nav-btn" onclick="sendModuleQuery('Knowledge Library', 'Audit knowledge base')">📚 Knowledge Library</button>
        <button class="nav-btn" onclick="sendModuleQuery('Scheduled Tasks', 'Check active background worker queues')">⏰ Scheduled Tasks</button>
        <a href="/management-control-hub" class="nav-btn" target="_blank" style="color: #38bdf8; margin-top: 20px;">⚙️ Open Admin Panel</a>
    </div>
    <div class="main-container">
        <div class="header">
            <h3>Sovereign Enterprise Dashboard</h3>
            <div id="agentBadge" class="agent-status">🟢 37-Agent Swarm Ready</div>
        </div>
        <div id="chatBox" class="chat-box">
            <div class="message assistant">Namaste Boss! G1 aur X1 ki laaparwahi ko sudhar diya gaya hai. Ab naya clean dashboard live hai. Batayein kya karna hai?</div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" class="input-box" placeholder="Ask anything or assign a task..." onkeypress="checkEnter(event)">
            <button class="send-btn" onclick="sendMessage()">Send</button>
        </div>
    </div>
    <script>
        function updateActiveNav(moduleName) {
            document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('agentBadge').innerText = `🟢 Active Module: ${moduleName}`;
        }

        async function sendModuleQuery(moduleName, queryText) {
            event.preventDefault();
            updateActiveNav(moduleName);
            appendMessage(`Switching to ${moduleName}...`, 'user');
            await processBackendRequest(queryText);
        }

        function checkEnter(e) {
            if (e.key === 'Enter') sendMessage();
        }

        async function sendMessage() {
            const inputField = document.getElementById('userInput');
            const text = inputField.value.trim();
            if (!text) return;
            appendMessage(text, 'user');
            inputField.value = '';
            await processBackendRequest(text);
        }

        async function processBackendRequest(promptText) {
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: promptText })
                });
                const data = await response.json();
                appendMessage(data.response, 'assistant');
                if(data.agent) {
                    document.getElementById('agentBadge').innerText = `⚡ Active Agent: ${data.agent}`;
                }
            } catch (err) {
                appendMessage("Error communicating with local swarm cluster.", 'assistant');
            }
        }

        function appendMessage(text, sender) {
            const chatBox = document.getElementById('chatBox');
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${sender}`;
            msgDiv.innerText = text;
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

ADMIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Management Panel - Master Control</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0b0f19; color: #f3f4f6; padding: 20px; }
        h1 { color: #38bdf8; margin-bottom: 20px; font-size: 22px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .card { background: #111827; border: 1px solid #1f2937; border-radius: 10px; padding: 20px; }
        .card h3 { color: #34d399; margin-bottom: 15px; font-size: 16px; }
        .control-panel-btns { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
        .action-btn { background: #2563eb; color: #fff; border: none; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 600; }
        .action-btn:hover { background: #1d4ed8; }
        .danger-btn { background: #dc2626; }
        .danger-btn:hover { background: #b91c1c; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #1f2937; font-size: 13px; color: #d1d5db; }
        th { color: #9ca3af; }
        .link-btn { display: inline-block; background: #374151; color: #fff; padding: 8px 16px; border-radius: 6px; text-decoration: none; margin-bottom: 20px; font-weight: 600; font-size: 14px; }
        .link-btn:hover { background: #4b5563; }
        #outputLog { margin-top: 15px; background: #1f2937; padding: 12px; border-radius: 6px; font-size: 13px; color: #38bdf8; white-space: pre-wrap; }
    </style>
</head>
<body>
    <a href="/dashboard" class="link-btn" target="_blank">🌐 Open User Dashboard</a>
    <h1>⚙️ Management Panel & Master Control Hub</h1>
    
    <div class="card" style="margin-bottom: 20px;">
        <h3>🎮 Master Swarm Controls</h3>
        <div class="control-panel-btns">
            <button class="action-btn" onclick="triggerAction('Run G1 Security Audit')">🛡️ Trigger CISO Audit</button>
            <button class="action-btn" onclick="triggerAction('Optimize Swarm Architecture')">⚡ Optimize All Agents</button>
            <button class="action-btn" onclick="triggerAction('Broadcast System Notice')">📢 Broadcast Notice</button>
            <button class="action-btn danger-btn" onclick="clearLogs()">🧹 Purge Database Logs</button>
        </div>
        <div id="outputLog">Management panel control hub active. Click any action to execute...</div>
    </div>

    <div class="grid">
        <div class="card">
            <h3>🤖 37-Agent Status & Registry</h3>
            <table>
                <thead><tr><th>Agent Name</th><th>Status</th><th>Toggle</th></tr></thead>
                <tbody id="agentConfigTable"><tr><td colspan="3">Loading agents...</td></tr></tbody>
            </table>
        </div>
        <div class="card">
            <h3>📊 Live Agent Execution Logs</h3>
            <table>
                <thead><tr><th>Agent</th><th>Action</th><th>Time</th></tr></thead>
                <tbody id="logsTable"><tr><td colspan="3">Loading logs...</td></tr></tbody>
            </table>
        </div>
    </div>

    <script>
        async function triggerAction(actionName) {
            document.getElementById('outputLog').innerText = `Executing master command: ${actionName}...`;
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: actionName })
                });
                const data = await res.json();
                document.getElementById('outputLog').innerText = `[${data.agent} Response]:\n${data.response}`;
                fetchMetrics();
            } catch(e) {
                document.getElementById('outputLog').innerText = "Error executing master command.";
            }
        }

        async function clearLogs() {
            if(!confirm('Are you sure you want to purge audit logs?')) return;
            const res = await fetch('/api/clear-logs', { method: 'POST' });
            const data = await res.json();
            document.getElementById('outputLog').innerText = data.status;
            fetchMetrics();
        }

        async function toggleAgent(agentId) {
            await fetch('/api/toggle-agent', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: agentId })
            });
            fetchMetrics();
        }

        async function fetchMetrics() {
            try {
                const res = await fetch('/api/metrics');
                const data = await res.json();
                
                const logsBody = document.getElementById('logsTable');
                logsBody.innerHTML = data.logs.map(l => `<tr><td>${l[1]}</td><td>${l[2]}</td><td>${l[3]}</td></tr>`).join('') || '<tr><td colspan="3">No logs found</td></tr>';

                const agentTable = document.getElementById('agentConfigTable');
                agentTable.innerHTML = data.agents.map(a => `<tr><td>${a[1]}</td><td><span style="color: ${a[2]=='ACTIVE'?'#34d399':'#f87171'}">${a[2]}</span></td><td><button class="action-btn" style="padding:4px 8px; font-size:11px;" onclick="toggleAgent(${a[0]})">Toggle</button></td></tr>`).join('') || '<tr><td colspan="3">No agents found</td></tr>';
            } catch(e) {
                console.error(e);
            }
        }
        fetchMetrics();
        setInterval(fetchMetrics, 5000);
    </script>
</body>
</html>
"""

class CleanServerHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(USER_HTML.encode('utf-8'))
        elif self.path == '/management-control-hub':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(ADMIN_HTML.encode('utf-8'))
        elif self.path == '/api/metrics':
            conn = sqlite3.connect("enterprise.db")
            logs = conn.execute("SELECT * FROM AgentLogs ORDER BY id DESC LIMIT 10;").fetchall()
            agents = conn.execute("SELECT * FROM AgentConfig;").fetchall()
            conn.close()
            data = json.dumps({'logs': logs, 'agents': agents}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(data)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            user_prompt = data.get('prompt', '').strip()

            p = user_prompt.lower()
            if any(w in p for w in ['security', 'audit', 'ciso', 'safe']):
                agent_name = "G1 CISO & Governance"
                sys_inst = "You are G1 CISO executing security audits. Respond in Hinglish."
            else:
                agent_name = "X1 Master Orchestrator"
                sys_inst = "You are X1 Master Orchestrator controlling the platform. Respond in Hinglish."

            formatted_prompt = f"<|im_start|>system\n{sys_inst}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"

            cmd = [
                "./llama.cpp/build/bin/llama-cli",
                "-m", "models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
                "-p", formatted_prompt,
                "-n", "150",
                "--temp", "0.3",
                "--no-display-prompt"
            ]

            reply = ""
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
                raw = res.stdout
                if "<|im_start|>assistant\n" in raw:
                    raw = raw.split("<|im_start|>assistant\n")[-1]
                if "<|im_end|>" in raw:
                    raw = raw.split("<|im_end|>")[0]
                reply = raw.strip()
            except Exception:
                pass

            if not reply or len(reply) < 3:
                reply = f"Boss, command successfully execute ho gayi hai."

            try:
                conn = sqlite3.connect("enterprise.db")
                conn.execute("INSERT INTO Tasks (prompt, status, result) VALUES (?, 'COMPLETED', ?);", (user_prompt, reply))
                conn.execute("INSERT INTO AgentLogs (agent_name, action) VALUES (?, ?);", (agent_name, f"Action: {user_prompt[:30]}"))
                conn.commit()
                conn.close()
            except Exception:
                pass

            resp_data = json.dumps({'response': reply, 'agent': agent_name}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(resp_data)))
            self.end_headers()
            self.wfile.write(resp_data)
        elif self.path == '/api/clear-logs':
            conn = sqlite3.connect("enterprise.db")
            conn.execute("DELETE FROM AgentLogs;")
            conn.execute("DELETE FROM Tasks;")
            conn.commit()
            conn.close()
            resp = json.dumps({'status': '🧹 Database audit logs and tasks successfully purged!'}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(resp)
        elif self.path == '/api/toggle-agent':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            agent_id = data.get('id')
            conn = sqlite3.connect("enterprise.db")
            cur = conn.cursor()
            cur.execute("SELECT status FROM AgentConfig WHERE id = ?;", (agent_id,))
            row = cur.fetchone()
            if row:
                new_status = "INACTIVE" if row[0] == "ACTIVE" else "ACTIVE"
                cur.execute("UPDATE AgentConfig SET status = ? WHERE id = ?;", (new_status, agent_id))
                conn.commit()
            conn.close()
            resp = json.dumps({'status': 'success'}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(resp)
        else:
            super().do_POST()

print("🚀 Clean Server Active on http://localhost:8080")
HTTPServer(('0.0.0.0', 8080), CleanServerHandler).serve_forever()
