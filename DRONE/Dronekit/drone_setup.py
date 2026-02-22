
#Monkey Patching

import sys
import collections

def fix_compatibility():
    """
    Fixes compatibility issues between Dronekit and Python 3.10+
    by mapping deprecated collection attributes to the new locations.
    """
    # Using the higher-level version check
    if sys.version_info >= (3, 10):
        import collections.abc
        # Link the old names to the new locations in collections.abc
        collections.MutableMapping = collections.abc.MutableMapping
        collections.Mapping = collections.abc.Mapping
        collections.Sequence = collections.abc.Sequence
        collections.Iterable = collections.abc.Iterable
        collections.Callable = collections.abc.Callable