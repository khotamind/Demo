import os

def write_file(path: str, content: str) -> str:
    """Writes or overwrites content to a specified file."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully written to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def read_file(path: str) -> str:
    """Reads content from a specified file."""
    try:
        if not os.path.exists(path):
            return f"Error: File '{path}' does not exist."
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
