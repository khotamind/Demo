with open("index.html", "r") as f:
    content = f.read()

old_js = """            // Simulated AI Agent Response
            setTimeout(() => {
                const aiDiv = document.createElement('div');
                aiDiv.className = 'message assistant';
                aiDiv.innerHTML = `<div class="message-bubble">I am processing your request through the enterprise multi-agent network...</div>`;
                chatContainer.appendChild(aiDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }, 600);"""

new_js = """            // Real Local Agent Response
            const aiDiv = document.createElement('div');
            aiDiv.className = 'message assistant';
            aiDiv.innerHTML = `<div class="message-bubble" id="loading">Thinking...</div>`;
            chatContainer.appendChild(aiDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;

            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: message })
            })
            .then(res => res.json())
            .then(data => {
                aiDiv.querySelector('.message-bubble').innerText = data.response;
                chatContainer.scrollTop = chatContainer.scrollHeight;
            })
            .catch(err => {
                aiDiv.querySelector('.message-bubble').innerText = "Execution Error.";
            });"""

if old_js in content:
    content = content.replace(old_js, new_js)
    with open("index.html", "w") as f:
        f.write(content)
    print("✅ UI JS updated successfully!")
else:
    print("⚠️ JS pattern not matched, manually updated API fetch.")
