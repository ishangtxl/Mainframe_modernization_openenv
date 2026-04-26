"""Legacy COBOL Migration Workbench."""

try:
    from .client import LegacyCobolEnv
    from .models import LegacyCobolState
except ImportError:
    from client import LegacyCobolEnv
    from models import LegacyCobolState

__all__ = ["LegacyCobolEnv", "LegacyCobolState"]
