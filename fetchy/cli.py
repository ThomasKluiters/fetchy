import argparse

import fetchy as fty

from PyInquirer import prompt


def download(
    packages_to_download,
    mirror,
    out_dir,
    distribution,
    version,
    packages_file,
    architecture,
    fetchy_dir,
    ppas,
    exclusions,
):
    prompts = []

    if not fty.is_os_supported():
        if distribution is None:
            prompts.append(
                {
                    "type": "list",
                    "message": "Sorry, your operating system is not currently supported, please select one:",
                    "name": "distribution",
                    "choices": ["ubuntu", "debian"],
                }
            )
        if version is None:
            prompts.append(
                {
                    "type": "input",
                    "name": "version",
                    "message": "Please enter the version of the operating system you'd like to use (e.g. `buster`):",
                }
            )
        if prompts:
            answers = prompt(prompts)
            if "distribution" in answers:
                distribution = answers["distribution"]
            if "version" in answers:
                version = answers["version"]

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

    dependencies_to_exclude = fty.gather_exclusions(exclusions)

    downloader = fty.Downloader(packages, out_dir=out_dir)
    downloader.download_package(packages_to_download, dependencies_to_exclude)


def main():
    parser = argparse.ArgumentParser(description="Fetchy: Download Linux packages.")
    parser.add_argument(
        "packages",
        metavar="PACKAGES",
        help="the package fetchy should download",
        nargs="+",
    )
    parser.add_argument(
        "--mirror",
        help="the default mirror to use, defaults to the best mirror fetchy can find",
    )
    parser.add_argument(
        "--exclude",
        help="dependency to exclude can either be a name or a file to read from",
        action="append",
        default=[],
    )
    parser.add_argument(
        "--ppa",
        help="a ppa to add to the repository of packages",
        action="append",
        default=[],
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

    download(
        args.packages,
        args.mirror,
        args.out,
        args.distribution,
        args.version,
        args.packages_file,
        args.architecture,
        args.fetchy_dir,
        args.ppa,
        args.exclude,
    )


if __name__ == "__main__":
    main()
