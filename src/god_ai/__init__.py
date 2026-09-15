"""Public SDK for the God AI hybrid terminal assistant."""

from .config import GodConfig, configure, get_config
from .decorators import heal
from .ghost import GhostExecutionError, do
from .llm import LLMClient, LLMError, LLMResponse
from .system import SystemSnapshot, system


class _GodFacade:
    """Small facade that keeps the ergonomic ``from god_ai import god`` API."""

    configure = staticmethod(configure)
    heal = staticmethod(heal)
    do = staticmethod(do)
    system = system


god = _GodFacade()

__all__ = [
    "GodConfig",
    "GhostExecutionError",
    "LLMClient",
    "LLMError",
    "LLMResponse",
    "SystemSnapshot",
    "configure",
    "get_config",
    "god",
    "heal",
    "do",
    "system",
]
__version__ = "0.1.0"