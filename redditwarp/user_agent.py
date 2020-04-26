
from typing import Optional
import re
from dataclasses import dataclass

BOT_USER_AGENT_PATTERN = r'''
^(?:(?P<platform>[\w-]+):)?

(?P<app_id>[\w-]+)

(?:(?(platform)[:/]|/)
(?P<version>[\w\d.-]+))?

(?:\ +\(\ *by\ +(?P<author>\S+).*\))?

(?:\ +.*)?$
'''
'''
# Valid
u_SuvaBot
u_SuvaBot some text
a_b-c some text
u_SuvaBot (by u/Pyprohly)
u_SuvaBot (by u/Pyprohly) some text
u_SuvaBot/16
u_SuvaBot/1.3-rc
u_SuvaBot/v1.3.5
u_SuvaBot/1.3.5 some text
u_SuvaBot/7 (  by  u/Pyprohly  )
console:u_SuvaBot
console:u_SuvaBot some text
console:a_b-c some text
console:u_SuvaBot (by u/Pyprohly)
console:u_SuvaBot (by u/Pyprohly) some text
console:u_SuvaBot/16
console:u_SuvaBot:1.3-rc
console:u_SuvaBot/v1.3.5
console:u_SuvaBot:1.3.5 some text
console:u_SuvaBot/1.2.0 (by u/Pyprohly)
console:u_SuvaBot:1.0.2 (by u/Pyprohly) some text

# Invalid
console:u_SuvaBot:/16
console:u_SuvaBot/:16
console/u_SuvaBot:v1
console/u_SuvaBot/v1
console:/u_SuvaBot/v1

# Check
u_SuvaBot/7 (bby  u/Pyprohly)
console:u_SuvaBot/1.2.0 (by u/Pyprohly)some text
'''

BOT_USER_AGENT_REGEX = re.compile(BOT_USER_AGENT_PATTERN, re.X)

BLACKLIST = [
	'scraping',
	'searchme',
]

FAULTY_LIST = [
	'curl',
]

@dataclass
class BotUserAgent:
	platform: Optional[str]
	app_id: str
	version: Optional[str]
	author: Optional[str]

	def __str__(self):
		pf = self.platform
		ap = self.app_id
		vn = self.version
		au = self.author
		return (
			f"{f'{pf}:' if pf else ''}"
			f"{ap}"
			f"{f'/{vn}' if vn else ''}"
			f"{f' (by {au})' if au else ''}"
		)

def parse(s):
	m = BOT_USER_AGENT_REGEX.match(s)
	if m:
		return BotUserAgent(**m.groupdict())
	return None
