from debian import deb822
import email.utils


def get_go_src_pkgs(filename):
    with open(filename) as f:
        pkgs = deb822.Sources.iter_paragraphs(f)
        go_src_pkgs = [
            i
            for i in pkgs
            if "Build-Depends" in i and "dh-golang" in i["Build-Depends"]
        ]
    return {i["Package"]: i for i in go_src_pkgs}


def main():
    testing_source_filename = "/var/lib/apt/lists/mirrors.tuna.tsinghua.edu.cn_debian_dists_testing_main_source_Sources"
    unstable_source_filename = "/var/lib/apt/lists/mirrors.tuna.tsinghua.edu.cn_debian_dists_unstable_main_source_Sources"
    testing_src_pkgs = get_go_src_pkgs(testing_source_filename)
    unstable_src_pkgs = get_go_src_pkgs(unstable_source_filename)
    diff = []
    for pkg in testing_src_pkgs:
        if pkg not in unstable_src_pkgs:
            raise Exception(pkg + "not in unstable")
        if testing_src_pkgs[pkg]["Version"] != unstable_src_pkgs[pkg]["Version"]:
            diff.append(
                (
                    pkg,
                    testing_src_pkgs[pkg]["Version"],
                    unstable_src_pkgs[pkg]["Version"],
                    email.utils.parseaddr(testing_src_pkgs[pkg]["Maintainer"])[-1],
                )
            )
    row_fmt = "{:>39}{:>32}{:>34}{:>52}"
    print(row_fmt.format("Package", "Testing", "Unstable", "Maintainer Email"))
    for pkg in diff:
        print(row_fmt.format(*pkg))


if __name__ == "__main__":
    main()
