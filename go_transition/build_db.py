from debian import deb822


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
    )
    """
    )
    c.commit()
    cur.close()


def walk_src_packages(fn, suite, c):
    cur = c.cursor()
    with open(fn) as f:
        for pkg in deb822.Sources.iter_paragraphs(f):
            if not ("Build-Depends" in pkg and "dh-golang" in pkg["Build-Depends"]):
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
    c.commit()
    cur.close()


def walk_bin_packages(fn, suite, arch, c):
    cur = c.cursor()
    with open(fn) as f:
        for pkg in BuiltUsing.iter_paragraphs(f):
            if not ("Built-Using" in pkg and "golang-" in pkg["Built-Using"]):
                continue
            for r in pkg.relations["built-using"]:
                row = (
                    pkg["Package"],
                    arch,
                    suite,
                    pkg["Version"],
                    r[0]["name"],
                    r[0]["version"][1],
                )
                cur.execute(
                    """
                INSERT INTO pkg (bin_pkg, arch, suite, version, built_using, built_using_version)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                    row,
                )
    c.commit()
    cur.close()


def build_db(conn, mirror):
    create_table(conn)
    s = "/var/lib/apt/lists/%s_debian_dists_testing_main_source_Sources" % mirror
    walk_src_packages(s, "testing", conn)
    s = "/var/lib/apt/lists/%s_debian_dists_testing_main_binary-amd64_Packages" % mirror
    walk_bin_packages(s, "testing", "amd64", conn)


if __name__ == "__main__":
    import sqlite3
    import sys

    db = "/tmp/go-transition.db"
    mirror = "mirrors.tuna.tsinghua.edu.cn"
    if len(sys.argv) == 3:
        path = sys.argv[1]
        mirror = sys.argv[2]
    build_db(sqlite3.connect(db), mirror)
