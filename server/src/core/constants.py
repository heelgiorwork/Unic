import re
from datetime import timezone
from pathlib import Path
from re import Pattern
from typing import Final

BASE_DIR: Final[Path] = Path(__file__).resolve().parents[2]
LOG_DIR: Final[Path] = BASE_DIR / "logs"

DOMAIN_REGEX: Final[str] = r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
URL_PATTERN: Pattern[str] = re.compile(
    r"https://(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&/=]*)"
)
USERNAME_PATTERN: Pattern[str] = re.compile(r"^@[a-zA-Z0-9_]{5,32}$")
DATETIME_FORMAT: Final[str] = "%d.%m.%Y %H:%M:%S"

API_V1: Final[str] = "/api/v1"

TIMEZONE: Final[timezone] = timezone.utc
