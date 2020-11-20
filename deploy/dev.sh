#!/bin/sh 

WHICH="dev"
PORT=""
if [ "$1" = "--api" ]; then
	PORT="-p 5000:5000"
    WHICH="api"
	shift
fi
IMAGE="mancalai-${WHICH}"

# docker run -it -v "$(pwd):/usr/src/app" mancalai-api

# docker run --rm -it -v "$(pwd):/usr/src/app"  mancalai-api python3  mancala/adversary.py nn1h128 nn3h80 
#  mancalai-dev python3  mancala/adversary.py nns1h128 nnx1h128 


docker run \
	-it \
	--rm \
	-v "/c/Users/Brady/OneDrive/Python/mancalai:/usr/src/app" \
	# -v "$(pwd):/usr/src/app" \
	${PORT} \
	"mancalai-dev" "$@" 
	# "${IMAGE}" "$@" 
