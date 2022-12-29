from __future__ import annotations

from abc import abstractmethod

import requests


class Request:
    def __init__(self, app, path, method, data, params, error_class, headers, extra):
        self.app = app
        self.path = path
        self.method = method
        self.data = data
        self.params = params
        self.error_class = error_class
        self.headers = headers
        self.extra = extra
        self._cur_i = 0

    def submit(self):
        url = '/'.join(p.strip('/') for p in (self.app.domain, self.app.api_prefix, self.path))
        r = getattr(requests, self.method)(url, json=self.data, params=self.params, headers=self.headers, **self.extra)
        if r.status_code // 100 != 2:
            raise self.error_class(r)
        return r


class RequestMiddleware:
    _next: RequestMiddleware | None

    def __init__(self):
        self._next = None

    def set_next(self, next: RequestMiddleware):
        self._next = next

    def next(self, request: Request):
        assert self._next is not None
        return self._next.handle(request)

    @abstractmethod
    def handle(self, request: Request):
        pass


class SubmitMiddleware(RequestMiddleware):
    def handle(self, request: Request):
        return request.submit()
