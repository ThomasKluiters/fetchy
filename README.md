# Fetchy - A Python utility to easily build minimal docker images
  
## Why Fetchy?

Fetchy can be used to build minimal docker images with the minimal set
of dependencies required, significantly reducing the size of your Docker
images.

Furthermore, it is possible to customize the operating system,
architecture and operating system version to fetch the latest (secure)
packages from a package mirror.

## Installing

Fetchy can be installed by running the following command:

```bash
pip install fetchy
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

Download required packages for libc6 into a specific directory

```bash
fetchy download --out libc-packages libc6
```

If you want to build a docker image based on another operating
system (debian stretch in this example), this is also possible:

```bash
fetchy dockerize --distribution debian --version stretch openssl
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
fetchy -dockerize -exclude exclusions.txt python3
```

Note: exclusion files MUST end with a .txt extension!

#### Using PPA's

If some packages are not available for your main mirror, try using a ppa:

Using a name:
```bash
fetchy dockerize --ppa deadsnakes python3.8
```

Using a URL:
```bash
fetchy dockerize --ppa https://deb.nodesource.com/node_10.x nodejs
```

Or both!
```bash
fetchy dockerize --ppa https://deb.nodesource.com/node_10.x --ppa deadsnakes python3.8 nodejs
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

### Backlog

- Docker integration [x]
