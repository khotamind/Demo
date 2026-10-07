import json
import os
from openai import OpenAI
from tools.shell_tools import execute_shell
from tools.file_tools import write_file, read_file

SYSTEM_PROMPT = """
You are an autonomous AI coding agent running inside Termux on Android.
Your job is to plan, code, execute, and fix issues autonomously using tools.

Available capabilities:
1. Run bash commands (execute_shell)
2. Read files (read_file)
3. Write files (write_file)

Always think step-by-step and verify your work by running commands.
"""

class AgentOrchestrator:
    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def run_step(self, user_input: str = None):
        if user_input:
            self.messages.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )
        reply = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": reply})
        return reply
