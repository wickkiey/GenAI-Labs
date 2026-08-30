from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    from .registry import register_tool
except ImportError:
    from registry import register_tool

GET_CURRENT_TIME_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Get the current date and time in a given IANA timezone.",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "IANA timezone name, e.g. 'Asia/Kolkata' or 'UTC'.",
                }
            },
            "required": ["timezone"],
            "additionalProperties": False,
        },
    },
}


@register_tool(GET_CURRENT_TIME_SCHEMA)
def get_current_time(timezone: str = "UTC") -> str:
    try:
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        return f"Error: unknown timezone '{timezone}'"
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
