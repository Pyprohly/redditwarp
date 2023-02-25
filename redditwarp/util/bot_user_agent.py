
from __future__ import annotations

import re

RECOMMENDED_BOT_USER_AGENT_PATTERN: str = r'''
^(?:(?P<platform>[\w-]+):)?

(?P<app_id>[\w-]+)

(?:(?(platform)[:/]|/)
(?P<version>[\w\d.-]+))?

(?:\ +\(\ *by\ +(?P<author>\S+).*\))?

(?:\ +.*)?$
'''
RECOMMENDED_BOT_USER_AGENT_REGEX: re.Pattern[str] = re.compile(RECOMMENDED_BOT_USER_AGENT_PATTERN, re.X)
