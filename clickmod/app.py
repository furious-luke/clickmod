from importlib.metadata import entry_points
import inspect
import os
from typing import Callable

import click
from rich.console import Console

from .middleware import RequestMiddleware, SubmitMiddleware, Request
from .errors import ApiError


class ClickModApp:
    name: str
    domain: str
    envname: str
    main: Callable
    api_prefix: str
    console: Console
    request_middleware: RequestMiddleware

    ENTRY_POINT_GROUP: str = "clickmod"

    def __init__(
            self,
            name: str,
            domain: str,
            envname: str | None = None,
            api_prefix: str | None = None,
            request_middleware: list[RequestMiddleware] | None = None
    ):
        self.name = name
        self.envname = envname or name.upper()
        self.domain = os.environ.get(f"{self.envname}_DOMAIN", domain)
        self.api_prefix = api_prefix or "api"
        self.console = Console()
        self.request_middleware = self._prepare_middleware(request_middleware, SubmitMiddleware)

        # TODO: Oh so ugly.
        @click.group()
        @click.pass_context
        def main(ctx):
            if not ctx.obj:
                ctx.obj = {}
            ctx.obj['app'] = self
        self.main = main

        self.load_plugins()

    def load_plugins(self):
        clickmod_eps = entry_points(group=self.ENTRY_POINT_GROUP)
        for ep in clickmod_eps:
            ep_main = ep.load()
            ep_main(self)

    def add_request_middleware(self, request_middleware: list[RequestMiddleware] | RequestMiddleware):
        self.request_middleware = self._prepare_middleware(request_middleware, self.request_middleware)

    def api_request(self, path, method, data=None, params=None, error_class=ApiError, headers=None, **kwargs):
        request = Request(
            self, path, method,
            data=data, params=params, error_class=error_class, headers=headers, extra=kwargs,
        )
        return self.request_middleware.handle(request)

    def _prepare_middleware(self, *middleware) -> RequestMiddleware:
        to_process = list(middleware)
        prev = None
        first = None
        while len(to_process):
            n = to_process.pop(0)
            if isinstance(n, (list, tuple)):
                to_process = list(n) + to_process
                continue
            if inspect.isclass(n):
                n = n()
            if prev:
                prev.set_next(n)
            prev = n
            if not first:
                first = n
        assert first is not None
        return first
