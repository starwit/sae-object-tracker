# You must run `poetry export` before building this
FROM python:3.13-slim AS build

RUN apt update && apt install --no-install-recommends -y \
    build-essential \
    git

COPY requirements.txt ./

RUN pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels

FROM python:3.13-slim

RUN apt update && apt install --no-install-recommends -y \
    libglib2.0-0 \
    libgl1 \
    libturbojpeg0 \
    git

WORKDIR /code

COPY requirements.txt ./

# This should be fine if and only if the wheels are generated based on the poetry exported requirements.txt (see above)
RUN --mount=type=bind,from=build,source=/wheels,target=/wheels \
    pip install /wheels/*

COPY main.py ./
COPY ./objecttracker ./objecttracker

CMD [ "python", "main.py" ]