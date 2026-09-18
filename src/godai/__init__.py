"""godai: a lazy, four-part toolkit for resilient AI-assisted Python work."""

from importlib import import_module

__version__ = "1.0.0"
__all__ = ["aura", "nexus", "aether", "apex"]

def __getattr__(name: str):
    """Load a sub-library only when it is first requested."""
    if name in __all__:
        module = import_module(f"godai.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module 'godai' has no attribute {name!r}")