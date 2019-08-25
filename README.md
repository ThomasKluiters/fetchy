[![Build Status](https://dev.azure.com/thomaskluiters0922/thomaskluiters/_apis/build/status/ThomasKluiters.fetchy?branchName=master)](https://dev.azure.com/thomaskluiters0922/thomaskluiters/_build/latest?definitionId=1&branchName=master)

# Fetchy - Minuscule images made trivial
  
## Why Fetchy?

Fetchy can be used to build minimal docker images with the minimal set
of dependencies required, significantly reducing the size of your Docker
images.

Fetchy will make it incredibly easy to build your docker
images. Simply using the CLI `fetchy dockerize <name>`. Try it!

Furthermore, it is possible to customize the operating system,
architecture and operating system version to fetch the latest (secure)
packages from a package mirror.

## How does Fetchy work?

Fetchy works by downloading debian / ubuntu packages based on some
parameter you supply Fetchy. For example, if you tell fetchy to use
ubuntu as a distribution and bionic as its version and download python
Fetchy will look for available packages under `python` and download the
packages required to run `python`. Then, if tasked to do so, Fetchy will
extract the files of all the packages and wrap them in a Docker image.

Fetchy will try to slim down the image by inspecting dependencies and remove
/include packages as it sees fit.

## Backlog

Currently the following features are being worked on:

- Direct installation of package through url
- Support redhat's archive
- Easy exclusions and inclusions of files
- Interactive management of packages
- Stability fixes

## Does Fetchy have any effect on my system?

A folder will be created under ~/.cache for caching.
Or, if specified under `$XDG_CACHE_HOME`.

## Installing

Fetchy can be installed by running the following command:

Any of:

```bash
pip3 install fetchy
```
```bash
pip install fetchy
```
```bash
python3 -m pip install fetchy
```

## Examples

Some existing images can be found here https://github.com/ThomasKluiters/fetchy-images 

Fetchy can be used as a command line utility, though, it
also offers an API.

Create a minimal docker image for a python environment based
on your current operating system and architecture.

```bash
fetchy dockerize python
```

You can specify multiple packages:

```bash
fetchy dockerize python3.6 postgresql
```

If you want to build a docker image based on another operating
system (debian stretch in this example), this is also possible:

```bash
fetchy dockerize --distribution debian --version stretch openssl
```

### Blueprints

You can also use blueprints to build images:

```yaml
architecture: amd64
base: scratch
codename: bionic
distribution: ubuntu
packages:
  exclude:
  - debconf
  fetch:
  - python
tag: builder
```

Call fetchy with:

```bash
fetchy blueprint blueprint.yml
```

### Advanced features

#### Excluding dependencies

If some packages are unwanted, you can simply exclude them:

Using a name:
```bash
fetchy dockerize --exclude dpkg --exclude perl-base python3
```

It is also possible to create an exclusion file, where each line
denotes a dependency that should not be included:


exclusions.txt
```
perl-base
dpkg
```

Using a name:
```bash
fetchy dockerize -exclude exclusions.txt python3
```

Note: exclusion files MUST end with a .txt extension!

#### Using PPA's

If some packages are not available for your main mirror, try using a ppa:

Using a name:
```bash
fetchy dockerize --ppa deadsnakes/ppa python3.8
```

Using a URL:
```bash
fetchy dockerize --ppa https://deb.nodesource.com/node_10.x nodejs
```

Or both!
```bash
fetchy dockerize --ppa https://deb.nodesource.com/node_10.x --ppa deadsnakes/ppa python3.8 nodejs
```

## Developing

Fetchy uses [poetry](https://github.com/sdispater/poetry) to build all sources and collect all requirements. 
The project can be set up through the following sequence of commands:

```bash
pip install poetry
git clone https://github.com/ThomasKluiters/fetchy
cd fetchy
poetry install
poetry shell
```
