with open("index.html", "r") as f:
    html = f.read()

# Update nav items with click actions
html = html.replace('<div class="nav-item"><span class="icon">🖼️</span> Images</div>', '<div class="nav-item" onclick="triggerService(\'Images\', \'Media Agent (P3)\')"><span class="icon">🖼️</span> Images</div>')
html = html.replace('<div class="nav-item"><span class="icon">📚</span> Library</div>', '<div class="nav-item" onclick="triggerService(\'Library\', \'Knowledge Agent (B2)\')"><span class="icon">📚</span> Library</div>')
html = html.replace('<div class="nav-item"><span class="icon">⏱️</span> Scheduled</div>', '<div class="nav-item" onclick="triggerService(\'Scheduled\', \'Cron/Ops Agent (In3)\')"><span class="icon">⏱️</span> Scheduled</div>')
html = html.replace('<div class="nav-item"><span class="icon">🔌</span> Plugins</div>', '<div class="nav-item" onclick="triggerService(\'Plugins\', \'Integration Agent (R7)\')"><span class="icon">🔌</span> Plugins</div>')
html = html.replace('<div class="nav-item"><span class="icon">📂</span> Projects</div>', '<div class="nav-item" onclick="triggerService(\'Projects\', \'Project Orchestrator (X1)\')"><span class="icon">📂</span> Projects</div>')
html = html.replace('<div class="nav-item"><span class="icon">💻</span> Codex (Code Engine)</div>', '<div class="nav-item" onclick="triggerService(\'Codex\', \'P2 Code Assistant\')"><span class="icon">💻</span> Codex (Code Engine)</div>')

script_add = """
    <script>
        function triggerService(serviceName, agentName) {
            const chatContainer = document.getElementById('chatContainer');
            const heroTitle = document.getElementById('heroTitle');
            if (heroTitle) heroTitle.style.display = 'none';

            const sysDiv = document.createElement('div');
            sysDiv.className = 'message assistant';
            sysDiv.innerHTML = `<div class="message-bubble" style="border: 1px solid #38bdf8;">📌 <b>[${agentName}]</b> Activated ${serviceName} module. Service is ready for execution.</div>`;
            chatContainer.appendChild(sysDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    </script>
</body>"""

if "function triggerService" not in html:
    html = html.replace("</body>", script_add)

with open("index.html", "w") as f:
    f.write(html)
print("✅ UI Buttons successfully connected to agents!")
