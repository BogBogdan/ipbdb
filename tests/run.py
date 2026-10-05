# Runs every check against a running node.
#
#   python run.py                       the local dev server on port 8001
#   python run.py http://165.227.150.114
#
# Nothing is written, the node is only read over http.

import sys
import time

from client import Site
import test_pages
import test_plots
import test_search
import test_tap

MODULES = [test_pages, test_plots, test_search, test_tap]


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8001'
    site = Site(base)
    print('testing %s' % base)

    failed = total = 0
    started = time.time()
    for module in MODULES:
        print('')
        print('== %s' % module.__name__)
        for name, ok, detail in module.checks(site):
            total += 1
            if not ok:
                failed += 1
            print('%-4s %-52s %s' % ('ok' if ok else 'FAIL', name, detail))

    print('')
    print('%d checks, %d failed, %.0f s' % (total, failed, time.time() - started))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
