FROM ollama/ollama:latest
WORKDIR /app
RUN echo "HELLO_FROM_DOCKERFILE"
RUN apt-get -y --no-install-recommends update
RUN apt-get -y --no-install-recommends install curl
RUN apt-get -y --no-install-recommends install jq
RUN apt-get -y --no-install-recommends install grep
RUN apt-get clean
COPY health /app/health
RUN chmod -R +x /app/health
HEALTHCHECK --interval=5s --timeout=5s --retries=1250 CMD /app/health/health.sh
COPY start.sh /usr/local/bin/start.sh
ENTRYPOINT ["/usr/local/bin/start.sh"]
