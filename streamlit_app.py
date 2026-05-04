import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Run the dashboard entry point
exec(open(Path(__file__).parent / "dashboard" / "app.py").read())
