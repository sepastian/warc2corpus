all: build

.PHONY: build
build:
	docker build -t sepastian/warc2corpus:latest .
