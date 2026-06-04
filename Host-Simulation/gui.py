"""Launcher GUI CuffnCode."""
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    src = Path(__file__).parent / "src" / "gui_app.py"
    raise SystemExit(subprocess.call([sys.executable, str(src)], cwd=Path(__file__).parent))
