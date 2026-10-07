import sqlite3
import os

db_path = "enterprise.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create Tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS Tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT NOT NULL,
    status TEXT DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS AgentLogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    action TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# Insert sample audit logs for test
cursor.execute("INSERT INTO Tasks (prompt, status) VALUES ('Run full system check', 'COMPLETED');")
cursor.execute("INSERT INTO AgentLogs (agent_name, action) VALUES ('G1 Security Agent', 'Approved System Check Task');")
cursor.execute("INSERT INTO AgentLogs (agent_name, action) VALUES ('X1 Orchestrator', 'Executed Multi-Agent Chained Workflow');")

conn.commit()
conn.close()

print("✅ Database Tables & Audit Logs Initialized Successfully!")
