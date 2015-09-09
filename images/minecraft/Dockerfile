FROM scratch
MAINTAINER "Ryan - faceless.saint@gmail.com"

#version information
ENV MINECRAFT_VERSION=1.8.8

#child containers inherit version information
ONBUILD ENV MINECRAFT_VERSION=${MINECRAFT_VERSION}

#download server from official sources
ADD ["https://s3.amazonaws.com/Minecraft.Download/versions/${MINECRAFT_VERSION}/minecraft_server.${MINECRAFT_VERSION}.jar", "/mnt/minecraft/"]

#specify volume location
VOLUME ["/mnt/minecraft"]
