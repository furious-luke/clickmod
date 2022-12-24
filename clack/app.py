from importlib.metadata import entry_points
from typing import Callable

import requests
from rich.console import Console

from .main import main
from .errors import ApiError


class ClackApp:
    name: str
    domain: str
    envname: str
    main: Callable
    api_prefix: str
    console: Console

    ENTRY_POINT_GROUP: str = "clack"

    def __init__(
            self,
            name: str,
            domain: str,
            envname: str | None = None,
            api_prefix: str | None = None,
    ):
        self.name = name
        self.domain = domain
        self.envname = envname or name.upper()
        self.api_prefix = api_prefix or "api"
        self.main = main
        self.console = Console()
        self.load_plugins()

    def load_plugins(self):
        clack_eps = entry_points(group=self.ENTRY_POINT_GROUP)
        for ep in clack_eps:
            ep_main = ep.load()
            ep_main(self)

    def api_request(self, path, method, data=None, params=None, error_class=ApiError, **kwargs):
        url = '/'.join(p.strip('/') for p in (self.domain, self.api_prefix, path))
        r = getattr(requests, method)(url, json=data, params=params, **kwargs)
        if r.status_code // 100 != 2:
            raise error_class(r)
        return r
