
from __future__ import annotations
from ...connector_SYNC import Connector as BaseConnector


class Connector(BaseConnector): pass


def new_connector() -> Connector: ...


name: str
version: str
