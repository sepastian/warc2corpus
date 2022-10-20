all: build

.PHONY: pyspark
pyspark: build
	docker run --rm -it -v $(CURDIR)/data:/w2c/data warc2corpus pyspark

.PHONY: console
console: build
	docker run --rm -it -v $(CURDIR)/data:/w2c/data --entrypoint=/bin/bash warc2corpus

.PHONY: sample-aut
sample-spark: build
	docker run --rm -it -v $(CURDIR)/data:/w2c/data \
	  --entrypoint=/spark/bin/spark-submit \
	  warc2corpus \
	  --py-files /aut/aut-1.1.0.zip \
	  --jars=/aut/aut-1.1.0-fatjar.jar \
	  sample/w2c_aut.py

.PHONY: sample-standalone
sample: build
	docker run --rm -it -v $(CURDIR)/data:/w2c/data \
	  -e PYTHONPATH=/aut/aut-1.1.0.zip:/w2c/lib \
	  --entrypoint=/usr/bin/python3 \
	  warc2corpus \
	  sample/w2c_standalone.py

.PHONY: build
build:
	docker build -t warc2corpus .

WARCFILE=data/uni_passau_de_pressemeldungen_`date +'%Y%m%dT%H%M%S'`
crawl:
	wget --recursive --level=1 --domains=www.uni-passau.de --adjust-extension --page-requisites --no-parent --no-verbose --reject-regex='.*/archiv/.*' --warc-file="$(WARCFILE)" 'https://www.uni-passau.de/bereiche/presse/pressemeldungen/'
