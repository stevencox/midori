#FROM midori/base:latest
FROM python:3.10-slim-bullseye

ENV API_PORT 8000
#ENV PYTHONPATH=/midori

RUN useradd -s /bin/bash midori
COPY --chown=midori . /midori
RUN mkdir -p /midori/logs

# Install all Python dependencies globally.
RUN /midori/bin/midori configure install

USER midori
CMD [ "/midori/bin/midorictl", "start", "api" ]
