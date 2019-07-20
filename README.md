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

## Examples

Fetchy can be used as a command line utility, though, it
also offers an API.

Download required packages for python3-minimal

```bash
fetchy python3.6-minimal
```

  

Download required packages for libc6 into a specific directory

```bash
fetchy --out libc-packages libc6
```

Download required packages for openssl for ubuntu

```bash
fetchy --distribution debian --version stretch openssl
```