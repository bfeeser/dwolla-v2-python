import requests

from dwollav2.response import Response
from dwollav2.version import version


def _items_or_iteritems(o):
    try:
        return o.iteritems()
    except:
        return o.items()

def _contains_file(o):
    if isinstance(o, dict):
        for k, v in _items_or_iteritems(o):
            if _contains_file(v):
                return True
        return False
    elif isinstance(o, tuple) or isinstance(o, list):
        for v in o:
            if _contains_file(v):
                return True
        return False
    else:
        return isinstance(o, file)

def token_for(_client):
    class Token:
        def __init__(self, opts = None, **kwargs):
            opts = kwargs if opts is None else opts
            self.access_token  = opts.get('access_token')
            self.refresh_token = opts.get('refresh_token')
            self.expires_in    = opts.get('expires_in')
            self.scope         = opts.get('scope')
            self.app_id        = opts.get('app_id')
            self.account_id    = opts.get('account_id')

        def post(self, body = None, **kwargs):
            body = kwargs if body is None else body
            if _contains_file(body):
                files = [(k, v) for k, v in _items_or_iteritems(body) if _contains_file(v)]
                data = [(k, v) for k, v in _items_or_iteritems(body) if not _contains_file(v)]
                return Response(requests.post(self._full_url(url), headers=self._headers(), files=files, data=data))
            else:
                return Response(requests.post(self._full_url(url), headers=self._headers(), json=body))

        def get(self, url, params = None, **kwargs):
            params = kwargs if params is None else params
            return Response(requests.get(self._full_url(url), headers=self._headers(), params=params))

        def delete(self, url):
            return Response(requests.delete(self._full_url(url), headers=self._headers()))

        def _headers(self):
            return {
                'accept': 'application/vnd.dwolla.v1.hal+json',
                'authorization': 'Bearer %s' % self.access_token,
                'user-agent': 'dwolla-v2-python %s' % version
            }

        def _full_url(self, path):
            if isinstance(path, dict):
                path = path['_links']['self']['href']

            if path.startswith(_client.api_url):
                return path
            elif path.startswith('/'):
                return _client.api_url + path
            else:
                return "%s/%s" % (_client.api_url, path)

    return Token
