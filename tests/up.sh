#!/usr/bin/env bash

if [ -z "$1" ]; then
    echo "Error: Wrong number of arguments passed!"
    exit 1
fi

#ping -W 1 -c 1 $1 > /dev/null
ping -W 1 -c 1 db1
exit
