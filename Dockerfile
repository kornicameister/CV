FROM pandoc/extra:3.7.0.2-alpine

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
