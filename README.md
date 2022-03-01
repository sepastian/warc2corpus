`warc2corpus` extracts text corpora from WARCs, according to a user-defined specification. The specification consists of CSS paths and (optional) transformations on the text extracted.

`warc2corpus` is best used with [Archives Unleashed Toolkit (AUT)](https://archivesunleashed.org/).


# Installation with Docker

AUT's `docker-aut` images serves as the base image for `warc2corpus`.

Since Docker images for Archives Unleashed Toolkit (AUT) are no longer available,
start by building `docker-aut` locally, see [instructions](https://github.com/archivesunleashed/docker-aut/).

```shell
git clone https://github.com/archivesunleashed/docker-aut.git
cd docker-aut
docker build -t aut .
```

Next, build the `warc2corpus` image localy.

```shell
git clone --branch integrate-with-aut git@github.com:sepastian/warc2corpus.git
cd warc2corpus
make build
```

Run the sample after building the image.

```shell
cd warc2corpus
make sample-spark
```
