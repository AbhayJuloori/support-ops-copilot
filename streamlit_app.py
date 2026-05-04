import os
import runpy
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))
os.chdir(root)
runpy.run_path(str(root / "dashboard" / "app.py"), run_name="__main__")
