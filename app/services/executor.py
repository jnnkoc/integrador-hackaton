import os
import subprocess
from pathlib import Path
from config import settings
import models


def execute_script(script: models.Script, params: dict) -> dict:
    scripts_dir = Path(os.environ.get("SCRIPTS_DIR", settings.scripts_dir))
    scripts_dir.mkdir(parents=True, exist_ok=True)

    script_path = scripts_dir / f"{script.name}.sh"
    script_path.write_text(script.content)
    script_path.chmod(0o755)

    param_values = [str(params.get(p, "")) for p in (script.parameters or [])]
    args = ["bash", str(script_path)] + param_values

    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "status": "success" if result.returncode == 0 else "error",
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Script timed out after 30 seconds",
            "exit_code": -1,
            "status": "timeout",
        }
