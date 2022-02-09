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
	--jars=/aut/target/aut-0.91.1-SNAPSHOT-fatjar.jar \
	sample/sample-spark.py

.PHONY: sample
sample: build
	docker run --rm -it -v $(CURDIR)/data:/w2c/data \
	--entrypoint=/usr/bin/python3 \
	warc2corpus \
	sample/sample.py

.PHONY: build
build:
	docker build -t warc2corpus .
