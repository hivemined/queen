#!/bin/sh
####
## Install Forge and Minecraft versions and update documentation
##
## Usage:
##    update.sh <forge installer> [--force]
####

#toggle git integration
__ENABLE_GIT=1

#simple input validation
if [ -e "$1" ]; then
    case "$1" in
        (*/forge-*-installer.jar);;
        (*)
            echo "ERROR: Specified file is not a Forge installer!"
            exit 1
            ;;
    esac
else
    echo "ERROR: Specified file does not exist!"
    exit 1
fi

#derive version information from given filename
MINECRAFT_VERSION=$(echo "$1" | sed "s/.*-\([0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\)-.*/\1/")
FORGE_VERSION=$(echo "$1" | sed "s/.*-\([0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\)-.*/\1/")

#fetch current version for comparison
OLD_VERSION=$(grep 'Current Version: ' 'README.md' | sed "s/^.*Current Version: \([0-9][0-9.]*[0-9]\).*/\1/")
echo -n "$OLD_VERSION  --->  "
echo "$FORGE_VERSION"

if [ "$OLD_VERSION" != "$FORGE_VERSION" ] || [ "$2" = --force ]; then
    echo "Updating from $OLD_VERSION to $FORGE_VERSION now!"

    #set minecraft version in Dockerfile
    sed -i "s/\(MINECRAFT_VERSION=\)[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*/\1${MINECRAFT_VERSION}/" Dockerfile

    #set forge version in Dockerfile and README.md
    sed -i "s/\(Current Version: \)[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*/\1${FORGE_VERSION}/" README.md
    sed -i "s/\(FORGE_VERSION=\)[0-9][0-9]*\.[0-9][0-9]*.[0-9][0-9]*\.[0-9][0-9]*/\1${FORGE_VERSION}/" Dockerfile

    cd src

    #clean previous installation files
    if [ $__ENABLE_GIT = 1 ]; then
        git rm -rf libraries forge-*-universal.jar minecraft_server.*.jar
    else
        rm -rf libraries forge-*-universal.jar minecraft_server.*.jar
    fi

    #install specified version of forge
    java -jar "../$1" --installServer
    rm -f "${1}.log"

    cd ..

    #update git repository with new tag
    if [ $__ENABLE_GIT = 1 ]; then
        git add README.md Dockerfile src/
        git commit -m "Update to $FORGE_VERSION" && git tag "$FORGE_VERSION" && git push && git push origin "$FORGE_VERSION"
    fi
else
    echo "Already up to date! Staying at version $OLD_VERSION"
fi
