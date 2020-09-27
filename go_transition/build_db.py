from debian import deb822
from mako.template import Template
from os.path import abspath, join, dirname
from go_transition import config
import subprocess
import re


class BuiltUsing(deb822.Packages):
    built_using = "built-using"
    _relationship_fields = [built_using]


def create_table(c):
    cur = c.cursor()
    cur.execute(
        """
    CREATE TABLE pkg (
     bin_pkg             text
    ,arch                text
    ,suite               text
    ,version             text
    ,built_using         text
    ,built_using_version text
    )
    """
    )
    cur.execute(
        """
    CREATE TABLE src (
     src_pkg text
    ,suite   text
    ,version text
    ,UNIQUE(src_pkg, suite) ON CONFLICT IGNORE
    )
    """
    )
    c.commit()
    cur.close()


def walk_src_packages(fn, suite, c):
    default_go_minor = 0
    cur = c.cursor()
    with open(fn, encoding="utf-8") as f:
        for pkg in deb822.Sources.iter_paragraphs(f):
            if pkg["Package"] == "golang-defaults":
                match = re.match("(\d+):(\d+)\.(\d+)", pkg["Version"])
                if match:
                    default_go_minor = int(match.group(3))
                continue
            if not (
                "Build-Depends" in pkg and "dh-golang" in pkg["Build-Depends"]
            ) and not (pkg["Package"].startswith("golang-1.")):
                continue
            if pkg.get("Extra-Source-Only") == "yes":
                continue
            row = (pkg["Package"], suite, pkg["Version"])
            cur.execute(
                """
                INSERT INTO src (src_pkg, suite, version) VALUES (?,?,?)
                """,
                row,
            )
        # dummy golang
        rows = [
            ("golang-1." + str(i), suite, "Bad") for i in range(6, default_go_minor)
        ]
        rows.append(("golang-pseudo", suite, "Bad"))
        cur.executemany(
            """
            INSERT INTO src (src_pkg, suite, version) VALUES (?,?,?)
            """,
            rows,
        )
        cur.execute(
            """
           UPDATE src SET version = (SELECT version FROM src WHERE src_pkg = ?)
           WHERE src_pkg = "golang-pseudo"
           """,
            ("golang-1." + str(default_go_minor),),
        )
    c.commit()
    cur.close()


def walk_bin_packages(fn, suite, arch, c):
    cur = c.cursor()
    with open(fn, encoding="utf-8") as f:
        for pkg in BuiltUsing.iter_paragraphs(f):
            if not ("Built-Using" in pkg and "golang-" in pkg["Built-Using"]):
                continue
            for r in pkg.relations["built-using"]:
                rows = [
                    (
                        pkg["Package"],
                        arch,
                        suite,
                        pkg["Version"],
                        r[0]["name"],
                        r[0]["version"][1],
                    )
                ]
                if r[0]["name"].startswith("golang-1."):
                    rows.append(
                        (
                            pkg["Package"],
                            arch,
                            suite,
                            pkg["Version"],
                            "golang-pseudo",
                            r[0]["version"][1],
                        )
                    )
                cur.executemany(
                    """
                INSERT INTO pkg (bin_pkg, arch, suite, version, built_using, built_using_version)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                    rows,
                )
    c.commit()
    cur.close()


def download():
    with open(
        abspath(
            join(
                dirname(__file__),
                "..",
                "apt",
                "etc",
                "apt",
                "sources.list.d",
                "sources.sources",
            )
        ),
        "w",
        encoding="utf-8",
    ) as f:
        f.write(
            Template(filename=abspath(join(dirname(__file__), "sources.tmpl"))).render(
                mirror=config.mirror, archs=config.archs, suite=config.suite
            )
        )
    subprocess.run(
        [
            "apt-get",
            "-qq",
            "-o",
            "Dir=" + abspath(join(dirname(__file__), "..", "apt")),
            "-o" "Dir::Etc::trustedparts=/etc/apt/trusted.gpg.d/",
            "update",
        ],
        check=True,
    )


def build_db(conn):
    create_table(conn)
    sources = "%s_debian_dists_%s_main_source_Sources" % (config.mirror, config.suite)
    walk_src_packages(
        abspath(
            join(dirname(__file__), "..", "apt", "var", "lib", "apt", "lists", sources)
        ),
        config.suite,
        conn,
    )
    for arch in config.archs:
        packages = "%s_debian_dists_%s_main_binary-%s_Packages" % (
            config.mirror,
            config.suite,
            arch,
        )
        walk_bin_packages(
            abspath(
                join(
                    dirname(__file__),
                    "..",
                    "apt",
                    "var",
                    "lib",
                    "apt",
                    "lists",
                    packages,
                )
            ),
            config.suite,
            arch,
            conn,
        )


def main(conn):
    download()
    build_db(conn)


if __name__ == "__main__":
    import sqlite3
    import sys

    db = "/tmp/go-transition.db"
    if len(sys.argv) == 2:
        path = sys.argv[1]
    main(sqlite3.connect(db))
