#!/bin/bash

if [ -e '/app/assets/scripts/install.sh' ]; then
    cd /app/assets/scripts/
    ./install.sh
else
    echo "No dependencies to install"
fi