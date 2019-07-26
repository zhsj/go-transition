from dataclasses import dataclass
from mako.template import Template
from os.path import abspath, join, dirname
import itertools
import time


@dataclass
class Src:
    name: str
    version: str


@dataclass
class Bin:
    name: str
    version: str
    using: dict

    def status(self, version: str) -> str:
        if all(i == version for i in self.using.values()):
            return "good"
        return "bad"


def get_pkgs(conn, suite):
    pkgs = []
    c = conn.cursor()
    for src_row, row in itertools.groupby(
        c.execute(
            """
    SELECT src.src_pkg, src.version, pkg.bin_pkg, pkg.version,
           pkg.arch, pkg.built_using_version
    FROM src JOIN pkg
    WHERE src.src_pkg = pkg.built_using
          AND src.suite = pkg.suite
          AND src.suite = '%s'
    """
            % suite
        ),
        lambda x: (x[0], x[1]),
    ):
        src = Src(src_row[0], src_row[1])
        bins = []
        for bin_row, arch_row in itertools.groupby(row, lambda x: (x[2], x[3])):
            archs = {}
            for arch in arch_row:
                archs[arch[4]] = arch[5]
            bins.append(Bin(bin_row[0], bin_row[1], archs))
        pkgs.append({"src": src, "bins": bins})
    return pkgs


def render(conn):
    args = {
        "date": time.strftime("%a, %d %b %Y %H:%M:%S %z", time.localtime()),
        "archs": [
            "amd64",
            # "arm64",
            # "armel",
            # "armhf",
            # "i386",
            # "mips",
            # "mips64el",
            # "mipsel",
            # "ppc64el",
            # "s390x",
        ],
        "pkgs": get_pkgs(conn, "testing"),
    }
    index = Template(
        filename=abspath(join(dirname(__file__), "templates", "index.html"))
    )
    with open(abspath(join(dirname(__file__), "..", "static", "index.html")), "w") as f:
        f.write(index.render(**args))


if __name__ == "__main__":
    import sqlite3
    import sys

    db = "/tmp/go-transition.db"
    if len(sys.argv) == 2:
        db = sys.argv[1]
    render(sqlite3.connect(db))
