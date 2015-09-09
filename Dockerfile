FROM debian:8
MAINTAINER "Ryan - faceless.saint@gmail.com"

LABEL hivemined.queen

COPY ["src", "/usr/local/bin/"]

COPY ["src/images", "/usr/local/src"]

ENTRYPOINT ["/usr/local/bin/main.py"]
