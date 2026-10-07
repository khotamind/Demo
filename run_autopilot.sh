#!/bin/bash
pkill -f "queue_server.py" 2>/dev/null
pkill -f "server.py" 2>/dev/null

echo "🤖 Launching Master Orchestrator in Autonomous Auto-Pilot Mode..."
nohup python queue_server.py > engine.log 2>&1 &
echo "✅ Auto-Pilot Active. 37 Agents operating autonomously."
