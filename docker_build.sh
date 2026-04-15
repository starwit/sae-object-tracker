#!/bin/bash

poetry export -o requirements.txt --without-hashes

docker build -t starwitorg/sae-object-tracker:local .

# Run with other components from the SAE compose project (set redis host to `redis`):
# `docker run -it --rm --network sae -v $(pwd)/settings.yaml:/code/settings.yaml starwitorg/sae-object-tracker:local`