# Fetchy - A Python utility to download debian packages
  
## Why Fetchy?

Fetchy can be used to download the absolute minimal dependencies required 
for a specific package. Fetchy aims to make it easier to acquire packages
for any architecture and any version of a package. Tools like `apt-get`
do not offer sufficient functionality to *only* download required packages
regardless of the architecture `apt-get` is running on.

## What can Fetchy be used for?

Fetchy can be used for the construction of Docker images. For example,
creating a docker image with *just* python3.6 which can be quite challenging
using existing tools.

## Installing

Fetchy can be installed by running the following command:

```bash
pip install fetchy
```

## Deveoping

Fetchy uses [poetry](https://github.com/sdispater/poetry) to build all sources and collect all requirements. 
The project can be set up through the following sequence of commands:

```bash
pip install poetry
git clone https://github.com/ThomasKluiters/fetchy
cd fetchy
poetry install
poetry shell
```

## Examples

Fetchy can be used as a command line utility, though, it
also offers an API.

Download required packages for python3-minimal

```bash
fetchy python3.6-minimal
```


Download required packages for python3.6 and postgresql

```bash
fetchy python3.6 postgresql
```

Download required packages for libc6 into a specific directory

```bash
fetchy --out libc-packages libc6
```

Download required packages for openssl for ubuntu

```bash
fetchy --distribution debian --version stretch openssl
```

### Advanced features

#### Excluding dependencies

If some packages are unwanted, you can simply exclude them:

Using a name:
```bash
fetchy --exclude dpkg --exclude perl-base python3
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
fetchy --exclude exclusions.txt python3
```

Note: exclusion files MUST end with a .txt extension!

#### Using PPA's

If some packages are not available for your main mirror, try using a ppa:

Using a name:
```bash
fetchy --ppa deadsnakes python3.8
```

Using a URL:
```bash
fetchy --ppa https://deb.nodesource.com/node_10.x nodejs
```

Or both!
```bash
fetchy --ppa https://deb.nodesource.com/node_10.x --ppa deadsnakes python3.8 nodejs
```

### Backlog

- Docker integration
