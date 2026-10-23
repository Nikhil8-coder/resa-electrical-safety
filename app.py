"""RESA Streamlit Entrypoint."""
import runpy
import sys
from pathlib import Path

# Ensure root and backend package are in sys.path
_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
_backend = _root / "backend"
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

if __name__ == "__main__":
    target = _root / "streamlit_app.py"
    runpy.run_path(str(target), run_name="__main__")
