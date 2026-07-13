.DEFAULT_GOAL := cv

SOURCE_FILES := $(wildcard src/*.yml)

CWD=${PWD}
BUILD_DIR=${CWD}/build

CONTAINER_WORK_DIR=/data
CONTAINER_BUILD_DIR=$(CONTAINER_WORK_DIR)/build

PANDOC=docker run --rm -v $(CWD):$(CONTAINER_WORK_DIR) -v $(BUILD_DIR):$(CONTAINER_BUILD_DIR) pandoc:latest
PANDOC_OPTS=--standalone -f "markdown+smart"
PANDOC_PDF_OPTS=$(PANDOC_OPTS) --pdf-engine=xelatex --template=template/cv.tex

YAML_TO_JSON=docker run -i --rm ingy/yaml-to-json

init:
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)
	rm -rf web/dist web/src/data/cv.json web/public/media

build_docker: Dockerfile
	docker build --pull -t pandoc -f $< .

build/cv.yml: cv.yml scripts/expand_includes.py init
	uv run scripts/expand_includes.py cv.yml > $@

build/cv.json: build/cv.yml init
	uv run python3 -c \
		"import yaml, json, pathlib, datetime; print(json.dumps(yaml.safe_load(pathlib.Path('build/cv.yml').read_text()), default=lambda o: o.isoformat() if isinstance(o, (datetime.date, datetime.datetime)) else str(o)))" \
		> build/cv.json

ifneq ("$(wildcard appendix.md)","")
appendix.pdf: init
	$(PANDOC) metadata.yml $(PANDOC_OPTS) \
		-f markdown \
		-t pdf \
		-B template/cv_before.tex \
		-A template/cv_after.tex \
		-o build/$@ \
		appendix.md
else
appendix.pdf:
endif

build/cv.eng.json: build/cv.json
	cp $< $@

build/cv.pl.json: build/cv.eng.json scripts/translate_cv.py
	uv run --with boto3 scripts/translate_cv.py $< $@

cv.pdf: build/cv.yml init build_docker
	$(PANDOC) build/cv.yml metadata.yml $(PANDOC_PDF_OPTS) -o build/$@

cv_full.pdf: clean init appendix.pdf cv.pdf
	test -e ./build/appendix.pdf && pdfunite build/cv.pdf build/appendix.pdf build/cv_with_appendix.pdf || exit 0

cv.json: build/cv.json
cv.eng.json: build/cv.eng.json
cv.pl.json: build/cv.pl.json

web: build/cv.json
	mkdir -p web/src/data web/public/media
	cp build/cv.json web/src/data/cv.json
	cp -r media/* web/public/media/
	find data/ -type f | sort | xargs cat | shasum | cut -d' ' -f1 > web/src/data/content-seed.txt
	cd web && npm run build
