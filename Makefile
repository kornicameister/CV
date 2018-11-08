.DEFAULT_GOAL := cv

SOURCE_FILES := $(wildcard src/*.yml)

CWD=${PWD}
BUILD_DIR=${CWD}/build

CONTAINER_WORK_DIR=/data
CONTAINER_BUILD_DIR=$(CONTAINER_WORK_DIR)/build

PANDOC=docker run --rm -v $(CWD):$(CONTAINER_WORK_DIR) -v $(BUILD_DIR):$(CONTAINER_BUILD_DIR) pandoc:latest
PANDOC_OPTS=--standalone --smart
PANDOC_PDF_OPTS=$(PANDOC_OPTS) --latex-engine=xelatex --template=template/cv.tex

clean:
	rm -rf $(BUILD_DIR)

build_docker:
	docker build -t pandoc .

init: clean build_docker
	mkdir -p $(BUILD_DIR)

build_appendix:
	test -f appendix.md && \
		$(PANDOC) metadata.yml $(PANDOC_OPTS)  \
		-f markdown \
		-B template/appendix_before.tex \
		-A template/appendix_after.tex \
		-o build/appendix.pdf \
		appendix.md

build_pdf:
	$(PANDOC) cv.yml $(PANDOC_PDF_OPTS) -o build/cv.pdf

cv: init build_appendix build_pdf
	test -f build/appendix.pdf && pdfunite build/cv.pdf build/appendix.pdf build/cv_with_appendix.pdf
