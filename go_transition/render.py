from mako.template import Template
from os.path import abspath, join, dirname
from go_transition import config
import itertools
import time


class Src:
    name = ""
    version = ""

    def __init__(self, name, version):
        self.name = name
        self.version = version


class Bin:
    name = ""
    version = ""
    using = {}

    def __init__(self, name, version, using):
        self.name = name
        self.version = version
        self.using = using

    def status(self, version):
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
            ORDER BY src.src_pkg, src.version, pkg.bin_pkg, pkg.version
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


def main(conn):
    args = {
        "date": time.strftime("%a, %d %b %Y %H:%M:%S %z", time.localtime()),
        "archs": config.archs,
        "pkgs": get_pkgs(conn, config.suite),
    }
    index = Template(
        filename=abspath(join(dirname(__file__), "templates", "index.html"))
    )
    with open(
        abspath(join(dirname(__file__), "..", "static", "index.html")),
        "w",
        encoding="utf-8",
    ) as f:
        f.write(index.render(**args))


if __name__ == "__main__":
    import sqlite3
    import sys

    db = "/tmp/go-transition.db"
    if len(sys.argv) == 2:
        db = sys.argv[1]
    main(sqlite3.connect(db))
