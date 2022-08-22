import subprocess

from debian import deb822


def deb_source():
    return (
        subprocess.check_output(
            [
                "apt-get",
                "indextargets",
                "--format",
                "$(FILENAME)",
                "Codename: sid",
                "ShortDesc: Sources",
            ]
        )
        .decode()
        .strip()
    )


def list_pkgs():
    # type: () -> dict[str, list[deb822.Sources]]
    pkgs = {}
    fn = deb_source()
    with open(fn, encoding="utf-8") as f:
        for pkg in deb822.Sources.iter_paragraphs(f):
            if pkg.get("Extra-Source-Only") == "yes":
                continue
            name = pkg["Package"]
            pkgs[name] = pkgs.get(name, []) + [pkg]
    return {
        k: v
        for k, v in pkgs.items()
        if "golang" in k and len(v) > 1 and len({pkg["Binary"] for pkg in v}) > 1
    }


if __name__ == "__main__":
    pkgs = list_pkgs()
    print(len(pkgs))
    for k, v in pkgs.items():
        print("%s: %s" % (k, {pkg["Binary"] for pkg in v}))

# vim: ts=4:sw=4:et
