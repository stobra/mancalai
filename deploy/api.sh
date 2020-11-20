#!/bin/sh 

WHICH="api"
PORT=""
if [ "$1" = "--api" ]; then
	PORT="-p 5000:5000"
    WHICH="api"
	shift
fi
IMAGE="mancalai-${WHICH}"


docker run -it --rm -p 127.0.0.1:5000:5000 "mancalai-api" "$@" 
	# -v "/c/Users/Brady/OneDrive/Python/mancalai:/usr/src/app" \
	# -v "$(pwd):/usr/src/app" \
	# "mancalai-api" "$@" 
	# "${IMAGE}" "$@" 
