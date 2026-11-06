"""Run the K Fund demonstration under the existing Render start command."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "modern_kfund"))
from server import app
