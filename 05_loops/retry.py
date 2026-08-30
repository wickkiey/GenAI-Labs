from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

try:
    from .trajectory import Trajectory
except ImportError:
    from trajectory import Trajectory


def run_retry(action: Callable[[str | None], str], max_attempts: int = 3) -> Trajectory:
    """Call `action(previous_error)` until it succeeds, feeding the last error back in.

    `action` should raise on failure (a tool error or a parse error) and return the
    result string on success. Stops on success or after `max_attempts`.
    """
    trajectory = Trajectory()
    error: str | None = None
    for attempt in range(1, max_attempts + 1):
        trajectory.iterations = attempt
        try:
            result = action(error)
        except Exception as exc:  # noqa: BLE001 - surfaced back into the next attempt
            error = str(exc)
            trajectory.steps.append({"attempt": attempt, "error": error})
            continue
        trajectory.steps.append({"attempt": attempt, "result": result})
        trajectory.final = result
        return trajectory

    trajectory.final = f"(failed after {max_attempts} attempts: {error})"
    return trajectory
