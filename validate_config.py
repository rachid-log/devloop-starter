"""Check a .watched.json file before Devloop reads it.

This check is stricter than Devloop on purpose. Devloop accepts aliases like 'bl' and quietly
replaces a bad watch_freq with 1h; this checker only accepts the exact form the README shows.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, List, Tuple, Union

ALLOWED_DOMAINS = ("General", "UX/UI", "SEO", "BL", "Security")

# A positive whole number, then m (minutes), h (hours) or d (days): 10m, 1h, 7d.
WATCH_FREQ_REGEX = re.compile(r"[1-9]\d*[mhd]")

REQUIRED_FIELDS = ("goal", "watch_freq", "domain", "active")


def validate_config(config: dict) -> List[str]:
    """Return every problem found in ``config``. An empty list means it is valid."""
    errors = [
        f"Missing required field: '{field}'" for field in REQUIRED_FIELDS if field not in config
    ]

    if "goal" in config:
        goal = config["goal"]
        if not isinstance(goal, str) or not goal.strip():
            errors.append(f"'goal' must be a non-empty string, got {goal!r}")

    if "watch_freq" in config:
        freq = config["watch_freq"]
        if not isinstance(freq, str) or not WATCH_FREQ_REGEX.fullmatch(freq):
            errors.append(
                f"'watch_freq' must be a positive number followed by m, h or d "
                f"(e.g. '10m', '1h', '1d'), got {freq!r}"
            )

    if "domain" in config:
        domain = config["domain"]
        if not isinstance(domain, str) or domain not in ALLOWED_DOMAINS:
            errors.append(
                f"'domain' must be one of {', '.join(ALLOWED_DOMAINS)} (exact case), got {domain!r}"
            )

    if "active" in config:
        active = config["active"]
        if type(active) is not bool:
            errors.append(f"'active' must be true or false, got {active!r}")

    return errors


def validate_config_file(path: Union[str, Path]) -> Tuple[bool, List[str]]:
    """Read and check one config file. Return ``(is_valid, errors)``."""
    path = Path(path)
    if not path.is_file():
        return False, [f"Config file does not exist: {path}"]

    try:
        content: Any = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return False, [f"Invalid JSON in {path}: {exc}"]

    if not isinstance(content, dict):
        return False, [f"{path} must be a JSON object {{ ... }}, got {type(content).__name__}"]

    errors = validate_config(content)
    return not errors, errors


def main(argv: List[str]) -> int:
    path = Path(argv[0]) if argv else Path(".watched.json")
    is_valid, errors = validate_config_file(path)
    if is_valid:
        print(f"{path} is valid.")
        return 0
    for error in errors:
        print(error, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
