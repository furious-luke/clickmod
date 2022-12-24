def api_request(path, method, data=None, params=None, error_class=ApiError, **kwargs):
    url = DOMAIN + API_PREFIX + path
    r = getattr(requests, method)(url, json=data, params=params, **kwargs)
    if r.status_code // 100 != 2:
        raise error_class(r)
    return r
