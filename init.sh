#!/bin/bash

cid_data = docker create --label Managed=Hivemined-Queen -v /var/hivemined/ scratch true
docker run --pull -it --privileged --volumes-from cid_data -v /var/run/docker.sock:/var/run/docker.sock \
    -v /var/lib/docker/:/var/lib/docker