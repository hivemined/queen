#!/bin/sh
docker run --privileged -v /var/run/docker.sock:/var/run/docker.sock --volumes-from \
	$(docker create --name hivemined-data --label hivemined.data -v /var/hivemined busybox true) \
	-it --name hivemined-queen --label hivemined.queen hivemined/queen $@
