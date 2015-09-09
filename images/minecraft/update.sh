#!/bin/sh
####
## Update to the latest Minecraft version and push changes to git
##
####

#toggle git integration
__ENABLE_GIT=1

#fetch current version for comparison
OLD_VERSION=$(grep 'Current Version: ' 'README.md' | sed "s/^.*Current Version: \([0-9][0-9.]*[0-9]\).*/\1/")
echo -n "$OLD_VERSION  --->  "

#fetch latest version information from official source
wget -q "https://s3.amazonaws.com/Minecraft.Download/versions/versions.json"
NEW_VERSION=$(grep '\"release\": ' 'versions.json' | sed "s/^.*\"\([0-9][0-9.]*[0-9]\)\".*/\1/")
echo "$NEW_VERSION"
rm "versions.json"

if [ "$OLD_VERSION" != "$NEW_VERSION" ]; then
    echo "Updating from $OLD_VERSION to $NEW_VERSION now!"

    #set minecraft version in Dockerfile and README.md
    sed -i "s/\(Current Version: \)[0-9][0-9.]*[0-9]/\1${NEW_VERSION}/" README.md
    sed -i "s/\(MINECRAFT_VERSION=\)[0-9][0-9.]*[0-9]/\1${NEW_VERSION}/" Dockerfile

    #update git repository with new tag
    if [ $__ENABLE_GIT = 1 ]; then
        git add README.md Dockerfile
        git commit -m "Update to $NEW_VERSION" && git tag "$NEW_VERSION" && git push
    fi
else
    echo "Already up to date! Staying at version $OLD_VERSION"
fi
