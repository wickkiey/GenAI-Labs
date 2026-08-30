"""Tool registry population: importing this package registers every built-in tool."""

try:
    from . import calculator, datetime_tool, filesystem, search, sqlite_tool  # noqa: F401
    from .registry import TOOL_REGISTRY
except ImportError:
    import calculator, datetime_tool, filesystem, search, sqlite_tool  # noqa: F401
    from registry import TOOL_REGISTRY

__all__ = ["TOOL_REGISTRY"]
