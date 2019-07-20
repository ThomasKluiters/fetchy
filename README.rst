========================================================================
Fetchy - A Python utility to download debian packages
========================================================================

Why Fetchy?
===============
Fetchy can be used to download the absolute minimal dependencies required
for a specific package. Fetchy aims to make it easier to acquire packages
for any architecture and any version of a package. Tools like `apt-get`
do not offer sufficient functionality to *only* download required packages
regardless of the architecture `apt-get` is running on.

What can Fetchy be used for?
=============================================
Fetchy can be used for the construction of Docker images. For example,
creating a docker image with *just* python3.6 can be a bit challenging.

We'd first have to start a seperate container with vanilla ubuntu and use
`apt-get` with the `download-only` flag. Furthermore, the packages downloaded
will be specific to the architecture the docker container is running as.


Examples
===============
