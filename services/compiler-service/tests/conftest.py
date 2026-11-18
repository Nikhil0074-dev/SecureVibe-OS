"""Load this service's `src` package ahead of sibling services during test collection."""
import sys
from pathlib import Path

service_root = str(Path(__file__).resolve().parents[1])
if service_root not in sys.path:
    sys.path.insert(0, service_root)

for module_name in tuple(sys.modules):
    if module_name == "src" or module_name.startswith("src."):
        del sys.modules[module_name]
