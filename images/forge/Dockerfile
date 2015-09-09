FROM scratch
MAINTAINER "Ryan - faceless.saint@gmail.com"

#version information
ENV MINECRAFT_VERSION=1.7.10 \
        FORGE_VERSION=10.13.4.1448

#child containers inherit version information
ONBUILD ENV MINECRAFT_VERSION=${MINECRAFT_VERSION} FORGE_VERSION=${FORGE_VERSION}

#copy local installation files
COPY ["src/", "/mnt/minecraft/"]

#specify volume location
VOLUME ["/mnt/minecraft"]
