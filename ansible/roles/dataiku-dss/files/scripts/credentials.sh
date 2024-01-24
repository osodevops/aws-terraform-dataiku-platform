#!/bin/env bash

host=github.com

# Get initial fingerprint from $host host
sshfprints=($(ssh-keyscan $host| ssh-keygen -lf - | awk '{ print $2}' | sed 's/SHA256://g' | sort))

# ----

# Get fingerprints from $host meta
metafprints=($(curl -s "https://api.$host/meta" | jq '.ssh_key_fingerprints' | awk '{ print $2}' | tr -d '",' | sort))

# Check if all fingerprints match
if [[ "${sshfprints[*]}"  == "${metafprints[*]}"  ]]
then
    echo "All fingerprints match."
else
    echo "Fingerprint match failed, please consult security team." 
    exit 1
fi

if [[ -f ~/.ssh/known_hosts ]]
then
    if [[ $(grep $host ~/.ssh/known_hosts) ]]
    then
        echo "Entries for $host already exist. Failing build"
        exit 1
    fi
fi

if [[ ! -d ~/.ssh ]]
    then
    mkdir ~/.ssh
    chmod 700 ~/.ssh
fi
ssh-keyscan $host >> ~/.ssh/known_hosts