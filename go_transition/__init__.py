import sys
from os.path import abspath, join, dirname

sys.path.extend(
    [
        abspath(join(dirname(__file__), "..", "third_party", "debian", "lib")),
        abspath(join(dirname(__file__), "..", "third_party", "mako")),
    ]
)
