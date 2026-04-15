# You must run `poetry export` before building this

FROM python:3.12-slim

RUN apt update && apt install --no-install-recommends -y \
    libglib2.0-0 \
    libgl1 \
    libturbojpeg0 \
    git

WORKDIR /code

COPY requirements.txt ./
RUN pip install -r ./requirements.txt

COPY main.py ./
COPY ./objecttracker ./objecttracker

CMD [ "python", "main.py" ]