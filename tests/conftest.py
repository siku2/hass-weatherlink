import sys
from pathlib import Path

CUSTOM_COMPONENTS_PATH = (Path(__file__) / "../../custom_components").resolve()
sys.path.append(str(CUSTOM_COMPONENTS_PATH))
