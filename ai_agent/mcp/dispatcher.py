import subprocess

def run_tool(cmd: list):
    """
    MCP / CLIツール実行レイヤー
    """

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }

    except Exception as e:
        return {
            "error": str(e)
        }