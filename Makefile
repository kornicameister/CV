.DEFAULT_GOAL := cv

SOURCE_FILES := $(wildcard src/*.yml)

CWD=${PWD}
BUILD_DIR=${CWD}/build

CONTAINER_WORK_DIR=/data
CONTAINER_BUILD_DIR=$(CONTAINER_WORK_DIR)/build

PANDOC=@docker run --rm -v $(CWD):$(CONTAINER_WORK_DIR) -v $(BUILD_DIR):$(CONTAINER_BUILD_DIR) pandoc:latest
PANDOC_OPTS=--standalone --smart
PANDOC_PDF_OPTS=$(PANDOC_OPTS) --latex-engine=xelatex --template=$(CWD)/template/cv.tex

YAML_TO_JSON=@docker run -i --rm ingy/yaml-to-json

init:
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)

build_docker: Dockerfile
	@docker build -t pandoc -f $< .

ifneq ("$(wildcard appendix.md)","")
appendix.pdf: init
	$(PANDOC) metadata.yml $(PANDOC_OPTS) \
		-f markdown \
		-t pdf \
		-B $(CWD)/template/cv_before.tex \
		-A t$(CWD)/emplate/cv_after.tex \
		-o $(BUILD_DIR)/$@ \
		appendix.md
else
appendix.pdf:
endif

cv.pdf: init build_docker
	$(PANDOC) cv.yml metadata.yml $(PANDOC_PDF_OPTS) -o $(BUILD_DIR)/$@

cv_full.pdf: clean init appendix.pdf cv.pdf
	test -e $(BUILD_DIR)/appendix.pdf && pdfunite build/cv.pdf build/appendix.pdf build/cv_with_appendix.pdf || exit 0

cv.json: init
	cat cv.yml | $(YAML_TO_JSON) | tee $(BUILD_DIR)/cv.json

