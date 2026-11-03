"""Check a .watched.json file before Devloop reads it.

This check is stricter than Devloop on purpose. Devloop accepts aliases like 'bl' and quietly
replaces a bad watch_freq with 1h; this checker only accepts the exact form the README shows.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, List, Tuple, Union

# Old single-area setting. Devloop now ignores it; 'facets' replaced it.
ALLOWED_DOMAINS = ("General", "UX/UI", "SEO", "BL", "Security")

# The areas Devloop can look at, as written in 'facets' (same keys as FACETS in devloop).
ALLOWED_FACETS = (
    "product", "ux", "bl", "growth", "content", "seo", "perf",
    "security", "reliability", "testing", "a11y", "analytics", "docs", "devex",
)
MAX_DOMAINS_PER_CYCLE = 5

# A positive whole number, then m (minutes), h (hours) or d (days): 10m, 1h, 7d.
WATCH_FREQ_REGEX = re.compile(r"[1-9]\d*[mhd]")

REQUIRED_FIELDS = ("goal", "watch_freq", "active")


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

    if "facets" in config:
        facets = config["facets"]
        if not isinstance(facets, list) or any(f not in ALLOWED_FACETS for f in facets):
            errors.append(
                f"'facets' must be a list of areas from {', '.join(ALLOWED_FACETS)} "
                f"([] means all of them), got {facets!r}"
            )

    if "domains_per_cycle" in config:
        count = config["domains_per_cycle"]
        if type(count) is not int or not 1 <= count <= MAX_DOMAINS_PER_CYCLE:
            errors.append(
                f"'domains_per_cycle' must be a whole number from 1 to {MAX_DOMAINS_PER_CYCLE}, "
                f"got {count!r}"
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
