FROM texlive/texlive:latest

RUN apt-get update && \
    apt-get upgrade -y -qq && \
    apt-get install \
      --no-install-recommends -y \
      fonts-font-awesome \
      latexmk \
      lmodern \
      pandoc \
      texlive-fonts-extra \
      texlive-fonts-recommended \
      texlive-latex-base \
      texlive-latex-extra \
      texlive-latex-recommended \
      texlive-luatex \
      texlive-pictures \
      texlive-xetex \
      xzdec \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /data

ENTRYPOINT ["/usr/bin/pandoc"]
CMD ["--help"]
