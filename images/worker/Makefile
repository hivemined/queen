.PHONY: install clean

ALL : src/mcchown

src/mcchown : src/mcchown.c
	gcc -o src/mcchown src/mcchown.c

install : Dockerfile src/cmd src/entrypoint src/entrypoint.conf src/mcchown src/skel.tgz
	docker build -t hivemined/worker .

clean :
	rm -f src/mcchown
