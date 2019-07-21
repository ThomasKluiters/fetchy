import argparse

import fetchy as fty


def main():
    parser = argparse.ArgumentParser(description="Fetchy: Download Linux packages.")
    parser.add_argument(
        "package", metavar="PACKAGE", help="the package fetchy should download"
    )
    parser.add_argument(
        "--mirror",
        help="the default mirror to use, defaults to the best mirror fetchy can find",
    )
    parser.add_argument(
        "--ppa", help="a ppa to add to the repository of packages", action="append"
    )
    parser.add_argument(
        "--out",
        help="the directory to download the packages into, defaults to ./packages",
        default="packages",
    )
    parser.add_argument(
        "--distribution",
        help="the distribution for which to fetch the packages, defaults to current distribution",
    )
    parser.add_argument(
        "--version",
        help="the distribution version for which to fetch the packages, defaults to current distribution version",
    )
    parser.add_argument(
        "--architecture",
        help="the architecture for which to fetch the packages, defaults to current architecture",
    )
    parser.add_argument("--packages-file", help="the packages file to read from")
    parser.add_argument(
        "--fetchy-dir",
        help="the home directory for fetchy",
        default=fty.get_fetchy_dir(),
    )
    args = parser.parse_args()

    (
        package,
        mirror,
        out_dir,
        distribution,
        version,
        packages_file,
        architecture,
        fetchy_dir,
        ppas,
    ) = (
        args.package,
        args.mirror,
        args.out,
        args.distribution,
        args.version,
        args.packages_file,
        args.architecture,
        args.fetchy_dir,
        args.ppa,
    )

    if mirror is None:
        mirror = fty.get_mirror(distribution)

    if packages_file is None:
        packages = fty.get_packages_control_file(
            distribution, version, architecture, mirror, fetchy_dir
        )
    else:
        packages = fty.Repository(packages_file, mirror)

    fty.Parser(packages).parse()

    for ppa in ppas:
        ppa_packages = fty.get_packages_control_file(
            distribution, version, architecture, fetchy_dir=fetchy_dir, ppa=ppa
        )

        fty.Parser(ppa_packages).parse()
        packages.merge(ppa_packages)

    downloader = fty.Downloader(packages, out_dir=out_dir)
    downloader.download_package(package)


if __name__ == "__main__":
    main()
