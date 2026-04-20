# You must run `poetry export` before building this
FROM python:3.13-slim AS build

RUN apt update && apt install --no-install-recommends -y \
    build-essential \
    git

# This needs to be generated with poetry export
COPY requirements.txt ./

RUN pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels

FROM python:3.13-slim

RUN apt update && apt install --no-install-recommends -y \
    libglib2.0-0 \
    libgl1 \
    libturbojpeg0 \
    git

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /code

# This needs to be generated with poetry export (same file as above)
COPY requirements.txt ./

# This should be fine if and only if the wheels are generated based on the poetry exported requirements.txt (see above)
RUN --mount=type=bind,from=build,source=/wheels,target=/wheels \
    pip install /wheels/*

COPY --chown=appuser:appgroup main.py ./
COPY --chown=appuser:appgroup ./objecttracker ./objecttracker
    
USER appuser
CMD [ "python", "main.py" ]