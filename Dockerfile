FROM pandoc/extra:3.8.0.0-alpine

RUN tlmgr init-usertree \
  && tlmgr update --self \
  && tlmgr install \
    fontawesome6 \
    ragged2e \
    xifthen \
    roboto \
    xstring \
  && mktexlsr

WORKDIR /data
VOLUME ["/data"]
