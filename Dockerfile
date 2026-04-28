FROM starwitorg/base-python-image:3.13.2-py3.13-ptr2.3.4 AS build

# Copy only files that are necessary to install dependencies
COPY poetry.lock poetry.toml pyproject.toml /code/

WORKDIR /code
RUN poetry install
    
# Copy the rest of the project
COPY . /code/

FROM python:3.13-slim

RUN apt update && apt install --no-install-recommends -y \
    libglib2.0-0 \
    libgl1 \
    libturbojpeg0 \
    git

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY --from=build --chown=appuser:appgroup /code /code

WORKDIR /code
    
USER appuser
ENV PATH="/code/.venv/bin:$PATH"
CMD [ "python", "main.py" ]