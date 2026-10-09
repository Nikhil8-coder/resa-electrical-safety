"""RESA Streamlit entrypoint alias.
Allows Streamlit Cloud to run via either 'app.py' or 'streamlit_app.py'.
"""
import runpy
from pathlib import Path

target = Path(__file__).parent / "streamlit_app.py"
runpy.run_path(str(target), run_name="__main__")
