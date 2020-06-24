
import re

UA_BLACKLIST = [
    'scraping',
    'searchme',
]
UA_FAULTY_LIST = [
    'curl',
]

BOT_USER_AGENT_PATTERN = r'''
^(?:(?P<platform>[\w-]+):)?

(?P<app_id>[\w-]+)

(?:(?(platform)[:/]|/)
(?P<version>[\w\d.-]+))?

(?:\ +\(\ *by\ +(?P<author>\S+).*\))?

(?:\ +.*)?$
'''
BOT_USER_AGENT_REGEX = re.compile(BOT_USER_AGENT_PATTERN, re.X)
