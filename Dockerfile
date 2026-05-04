# Single image for both poller and bot — entrypoint chosen via compose `command`.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# ca-certificates so Python's ssl module finds a trust store (slim has none).
RUN apt-get update -qq \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --upgrade pip \
 && pip install .

COPY src/ ./src/
RUN pip install -e .

CMD ["python", "-c", "print('vyklik image — set a command in compose')"]
