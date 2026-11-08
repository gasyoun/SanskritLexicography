"""Collection order + import path for the split window-selftest suite (H7241).

Importing `_support` first is deliberate: it establishes the production isolation
guard before any repo module is imported (same contract as the old selftest header).
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import _support  # noqa: E402,F401


def pytest_collection_modifyitems(session, config, items):
    """Run in the legacy `main()` order, so pass/fail parity is order-for-order."""
    order = {name: index for index, name in enumerate(_support.ORIGINAL_ORDER)}
    items.sort(key=lambda item: order.get(item.name, len(order)))
