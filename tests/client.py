# Reads pages from a running node, used by every test module.

import json
import urllib.error
import urllib.request


class Site:
    def __init__(self, base):
        self.base = base.rstrip('/')

    def fetch(self, path, timeout=240):
        # status and raw body, an http error is a result like any other
        try:
            with urllib.request.urlopen(self.base + path, timeout=timeout) as response:
                return response.getcode(), response.read()
        except urllib.error.HTTPError as error:
            return error.code, error.read()

    def text(self, path, timeout=240):
        status, body = self.fetch(path, timeout)
        return status, body.decode('utf-8', 'replace')

    def json(self, path, timeout=240):
        status, body = self.fetch(path, timeout)
        if status != 200:
            return status, None
        try:
            return status, json.loads(body)
        except ValueError:
            return status, None


def listed(items, limit=8):
    # short tail of offending ids for a failure line
    shown = ', '.join(str(item) for item in items[:limit])
    return shown + (' and %d more' % (len(items) - limit) if len(items) > limit else '')
