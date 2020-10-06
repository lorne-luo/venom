import sys
from pathlib import Path

path = Path(__file__)
sys.path.append(str(path.parent.parent))