FROM midori/base:latest

ENV API_PORT=8000
ENV PYTHONPATH=/midori:/containernet

RUN mkdir -p /midori/logs
#RUN useradd -s /bin/bash midori
#RUN chown -R midori:midori /midori

EXPOSE $API_PORT
#USER midori
WORKDIR /containernet
CMD [ "/midori/bin/midorictl", "start" ]
