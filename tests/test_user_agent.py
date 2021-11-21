
from typing import TypeVar, Type, Optional, Sequence, Tuple

from dataclasses import dataclass

from redditwarp.util.user_agent import BOT_USER_AGENT_REGEX

@dataclass
class BotUserAgent:
    platform: Optional[str]
    app_id: str
    version: Optional[str]
    author: Optional[str]

    T = TypeVar('T', bound='BotUserAgent')

    @classmethod
    def parse(cls: Type[T], s: str) -> Optional[T]:
        m = BOT_USER_AGENT_REGEX.match(s)
        if m:
            return cls(**m.groupdict())
        return None

    def __str__(self) -> str:
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

def test_bot_user_agent_regex() -> None:
    valid: Sequence[Tuple[str, BotUserAgent]] = [
        ('u_SuvaBot', BotUserAgent(None, 'u_SuvaBot', None, None)),
        ('u_SuvaBot some text', BotUserAgent(None, 'u_SuvaBot', None, None)),
        ('a_b-c some text', BotUserAgent(None, 'a_b-c', None, None)),
        ('u_SuvaBot (by u/Pyprohly)', BotUserAgent(None, 'u_SuvaBot', None, 'u/Pyprohly')),
        ('u_SuvaBot (by u/Pyprohly) some text', BotUserAgent(None, 'u_SuvaBot', None, 'u/Pyprohly')),
        ('u_SuvaBot/16', BotUserAgent(None, 'u_SuvaBot', '16', None)),
        ('u_SuvaBot/1.3-rc', BotUserAgent(None, 'u_SuvaBot', '1.3-rc', None)),
        ('u_SuvaBot/v1.3.5', BotUserAgent(None, 'u_SuvaBot', 'v1.3.5', None)),
        ('u_SuvaBot/1.3.5 some text', BotUserAgent(None, 'u_SuvaBot', '1.3.5', None)),
        ('u_SuvaBot/7 (  by  u/Pyprohly  )', BotUserAgent(None, 'u_SuvaBot', '7', 'u/Pyprohly')),
        ('u_SuvaBot/7 (bby  u/Pyprohly)', BotUserAgent(None, 'u_SuvaBot', '7', None)),
        ('console:u_SuvaBot', BotUserAgent('console', 'u_SuvaBot', None, None)),
        ('console:u_SuvaBot some text', BotUserAgent('console', 'u_SuvaBot', None, None)),
        ('console:a_b-c some text', BotUserAgent('console', 'a_b-c', None, None)),
        ('console:u_SuvaBot (by u/Pyprohly)', BotUserAgent('console', 'u_SuvaBot', None, 'u/Pyprohly')),
        ('console:u_SuvaBot (by u/Pyprohly) some text', BotUserAgent('console', 'u_SuvaBot', None, 'u/Pyprohly')),
        ('console:u_SuvaBot/16', BotUserAgent('console', 'u_SuvaBot', '16', None)),
        ('console:u_SuvaBot:1.3-rc', BotUserAgent('console', 'u_SuvaBot', '1.3-rc', None)),
        ('console:u_SuvaBot/v1.3.5', BotUserAgent('console', 'u_SuvaBot', 'v1.3.5', None)),
        ('console:u_SuvaBot:1.3.5 some text', BotUserAgent('console', 'u_SuvaBot', '1.3.5', None)),
        ('console:u_SuvaBot/1.2.0 (by u/Pyprohly)', BotUserAgent('console', 'u_SuvaBot', '1.2.0', 'u/Pyprohly')),
        ('console:u_SuvaBot:1.0.2 (by u/Pyprohly) some text', BotUserAgent('console', 'u_SuvaBot', '1.0.2', 'u/Pyprohly')),
        ('console:u_SuvaBot/1.2.0 (by u/Pyprohly)some text', BotUserAgent('console', 'u_SuvaBot', '1.2.0', None)),
    ]
    for strr, ua in valid:
        assert BotUserAgent.parse(strr) == ua

    invalid: Sequence[str] = [
        "console:u_SuvaBot:/16",
        "console:u_SuvaBot/:16",
        "console/u_SuvaBot:v1",
        "console/u_SuvaBot/v1",
        "console:/u_SuvaBot/v1",
    ]
    for strr in invalid:
        assert BotUserAgent.parse(strr) is None
