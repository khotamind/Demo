import subprocess

def execute_shell(command: str) -> str:
    """Executes bash commands in Termux and returns STDOUT/STDERR."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
        return output if output.strip() else "Command executed successfully with no output."
    except subprocess.TimeoutExpired:
        return "Error: Command execution timed out (120s limit)."
    except Exception as e:
        return f"Error executing command: {str(e)}"
