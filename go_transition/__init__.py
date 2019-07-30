import sys
from os.path import abspath, join, dirname

sys.path.extend(
    [
        abspath(join(dirname(__file__), "..", "third_party", "chardet")),
        abspath(join(dirname(__file__), "..", "third_party", "debian", "lib")),
        abspath(join(dirname(__file__), "..", "third_party", "mako")),
        abspath(join(dirname(__file__), "..", "third_party", "python-apt")),
    ]
)
