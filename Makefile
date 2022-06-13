all: build

.PHONY: pyspark
pyspark: build
	docker run --rm -it -v $(CURDIR)/data:/w2c/data warc2corpus pyspark

.PHONY: console
console: build
	docker run --rm -it -v $(CURDIR)/data:/w2c/data --entrypoint=/bin/bash warc2corpus

.PHONY: sample-spark
sample-spark: build
	docker run --rm -it -v $(CURDIR)/data:/w2c/data \
	  --entrypoint=/spark/bin/spark-submit \
	  warc2corpus \
	  --py-files /aut/target/aut.zip \
	  --jars=/aut/target/aut-1.0.1-SNAPSHOT-fatjar.jar \
	  sample/up_pressemeldungen.py

.PHONY: sample
sample: build
	docker run --rm -it -v $(CURDIR)/data:/w2c/data \
	  --entrypoint=/usr/bin/python3 \
	  warc2corpus \
	  sample/sample.py


.PHONY: build
build:
	docker build -t warc2corpus .

WARCFILE=data/uni_passau_de_pressemeldungen_`date +'%Y%m%dT%H%M%S'`
crawl:
	wget --recursive --level=1 --domains=www.uni-passau.de --adjust-extension --page-requisites --no-parent --no-verbose --reject-regex='.*/archiv/.*' --warc-file="$(WARCFILE)" 'https://www.uni-passau.de/bereiche/presse/pressemeldungen/'
