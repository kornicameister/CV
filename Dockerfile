FROM vipintm/xelatex:latest

RUN apt-get update && \
    apt-get install pandoc --no-install-recommends -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /data

ENTRYPOINT ["/usr/bin/pandoc"]
CMD ["--help"]
