FROM debian:8
MAINTAINER "Ryan - faceless.saint@gmail.com"

COPY ["src", "/usr/local/bin/"]

COPY ["src/worker", "src/drone", "/usr/local/src/"]

ENTRYPOINT ["/usr/local/bin/main.py"]
