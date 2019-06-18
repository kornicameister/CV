.DEFAULT_GOAL := cv

SOURCE_FILES := $(wildcard src/*.yml)

CWD=${PWD}
BUILD_DIR=${CWD}/build

CONTAINER_WORK_DIR=/data
CONTAINER_BUILD_DIR=$(CONTAINER_WORK_DIR)/build

PANDOC=docker run --rm -v $(CWD):$(CONTAINER_WORK_DIR) -v $(BUILD_DIR):$(CONTAINER_BUILD_DIR) pandoc:latest
PANDOC_OPTS=--standalone --smart
PANDOC_PDF_OPTS=$(PANDOC_OPTS) --latex-engine=xelatex --template=template/cv.tex

init:
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)

build_docker: Dockerfile
	docker build -t pandoc -f $< .

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

cv.pdf: init build_docker
	$(PANDOC) cv.yml $(PANDOC_PDF_OPTS) -o build/$@

cv_full.pdf: clean init appendix.pdf cv.pdf
	test -e ./build/appendix.pdf && pdfunite build/cv.pdf build/appendix.pdf build/cv_with_appendix.pdf || exit 0

cv.json: init
	cat cv.yml | docker run -i --rm -p 80:8080 ingy/yaml-to-json >> build/cv.json

