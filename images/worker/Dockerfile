FROM hivemined/jre
MAINTAINER "Ryan - faceless.saint@gmail.com"

#setup static file structure
ADD ["src/skel.tgz", "/"]

#add script files
COPY ["src/entrypoint.conf", "/usr/local/etc/"]
COPY ["src/cmd", "src/entrypoint", "src/mcchown", "/usr/local/bin/"]

#setup user data and file permissions
RUN useradd minecraft -d /opt/minecraft && chmod 4755 /usr/local/bin/mcchown && \
    chown -R minecraft:minecraft /opt/minecraft /mnt/minecraft /mnt/minecraft-etc /mnt/minecraft-var
USER minecraft

#define volumes and network ports
VOLUME ["/mnt/minecraft-etc", "/mnt/minecraft-var"]
EXPOSE 25565

#container initialization
WORKDIR /opt/minecraft
ENTRYPOINT ["/usr/local/bin/entrypoint"]
