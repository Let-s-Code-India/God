"""godaix: a lazy, five-part toolkit for resilient AI-assisted Python work."""

from importlib import import_module

__version__ = "1.0.3"
__all__ = ["aura", "nexus", "aether", "apex", "aix"]

def __getattr__(name: str):
    """Load a sub-library only when it is first requested."""
    if name in __all__:
        module = import_module(f"godaix.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module 'godaix' has no attribute {name!r}")