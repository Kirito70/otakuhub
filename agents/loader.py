"""
agents/loader.py – shared loader for VS Code (Open‑Code) and Copilot.

The Open‑Code extension expects a callable `load_agent(name: str) -> ModuleType`.
We read `agents/manifest.json`, locate the entry point, and import the module
using importlib.  All tool definitions are already available in the global
`functions` namespace (the same as Claude’s runtime).
"""

import importlib.util
import json
import pathlib
from types import ModuleType
from typing import Dict

MANIFEST_PATH = pathlib.Path(__file__).parent / "manifest.json"

def _read_manifest() -> Dict:
    with MANIFEST_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def load_agent(name: str) -> ModuleType:
    """Return the imported Python module for the requested agent.

    Raises:
        ValueError: If the agent name is not present in the manifest.
        ImportError: If the entry point cannot be imported.
    """
    manifest = _read_manifest()
    for agent in manifest.get("agents", []):
        if agent.get("name") == name:
            entry = pathlib.Path(agent["entry_point"]).resolve()
            spec = importlib.util.spec_from_file_location(name, entry)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load agent '{name}' from {entry}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore
            return module
    raise ValueError(f"Agent '{name}' not found in manifest")
