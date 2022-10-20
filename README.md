# warc2corpus

`warc2corpus` extracts text corpora from WARCs or HTML pages, according to a user-defined specification, or spec. The spec consists of CSS paths and (optional) transformations on the text extracted.

`warc2corpus` is best used with [Archives Unleashed Toolkit (AUT)](https://archivesunleashed.org/).


## Installation

The easiest way to use warc2corpus is to build and use a Docker image.

### Docker Images

AUT's `docker-aut` image, version 1.x.x, serves as the base image for `warc2corpus`.

_Note: Since pre-built Docker images for Archives Unleashed Toolkit (AUT) are no longer available, start by building `docker-aut` locally, see [instructions](https://github.com/archivesunleashed/docker-aut/)._

```shell
git clone https://github.com/archivesunleashed/docker-aut.git
cd docker-aut
git checkout 1.x.x     # checkout the 1.x.x branch
docker build -t aut .  # build AUT Docker image
```

Next, build the `warc2corpus` image locally.

```shell
git clone git@github.com:sepastian/warc2corpus.git
cd warc2corpus
make build
```

You are now ready to use warc2corpus.

## Usage

There are two ways of using warc2corpus: standalone or within AUT. In standalone mode, scripts are run using Python3. When using warc2corpus withing AUT, scripts are run using `spark-submit`.

### Standalone warc2corpus

Given a single HTML page containing a news article and a spec, a Python3 script makes use of warc2corpus to extract the date of release, as shown in the following example.

```python3
import warc2corpus as w2c
import dateparser as dp
import json

# Warc2corpus spec definig extractors.
spec= {
  'extracts': [
    {
      'name': 'released_at',
      'css_path': 'header time',
      'f': lambda m: dp.parse(m[0]['datetime'].strip(), date_formats=['%d. %B %Y']).isoformat()
    }
  ]
}
with open('file.html','r',encoding='utf-8') as f:
    html= f.read()
    result= w2c.apply(html, spec)
    print(json.dumps(result))

# Output:
# [
#   {
#     "css_path": "header time",
#     "name": "released_at",
#     "value": "2022-02-14T17:04:21"
#   }
# ]
```

A complete example can be found in [`sample/w2c_standalone.py`](sample/w2c_standalone.py). The sample can be run using a make target or by invoking `docker`.

```shell
cd warc2corpus/

# Run sample using make target.
make sample-standalone

# Alternatively, run sample using docker run.
docker run --rm -it \
  -v $(CURDIR)/data:/w2c/data \
  -e PYTHONPATH=/aut/aut-1.1.0.zip:/w2c/lib \
  --entrypoint=/usr/bin/python3 \
  warc2corpus \
    sample/w2c_standalone.py
```

### warc2corpus within AUT

For processing potentially large WARC files containing many HTML sites, it is recommended to run warc2corpus within AUT. Instead of reinventing the wheel, let AUT handle WARC files. Under the hat, Apache Spark is used for heavy data lifting.

In this example, a script processes a WARC file containing several HTML pages. The script is run using `spark-submit`. Not all HTML pages inside the WARC may be of interest. Warc2corpus allows specifying a regular expression, to select HTML pages to process by URL.

```python3
import json
import dateparser as dp
from pathlib import Path
from warc2corpus import run

# Warc2corpus will only process HTML pages within 
# the WARC with a URL matching this regex.
url_regex = ".+/pressemeldungen/meldung/detail/[a-z]+"

# Warc2corpus spec defining extractors.
spec= [
  {
    'extracts': [
      {
        'name': 'released_at',
        'css_path': '[itemprop~="datePublished"]',
        'f': lambda m: dp.parse(m[0]['datetime'].strip(), date_formats=['%d. %B %Y']).isoformat()
      }
    ]
  }
]

# Select HTML pages from WARC by regex, apply spec only 
# on pages with a url matching the regex supplied.
df = run(warc_file, config, url_regex=url_regex)

# Write results to console, in JSON format.
print(df.toJSON().collect())
```

A complete example can be found in [`sample/w2c_aut.py`](sample/w2c_aut.py). The sample can be run using a make target or by invoking `docker`.

```shell
cd warc2corpus/

# Run sample using make target.
make sample-aut

# Alternatively, run sample using docker run.
docker run --rm -it \
  -v $(CURDIR)/data:/w2c/data \
  --entrypoint=/spark/bin/spark-submit \
  warc2corpus \
    --py-files /aut/aut-1.1.0.zip \
    --jars=/aut/aut-1.1.0-fatjar.jar \
    sample/w2c_aut.py
```

## Spec Format

Warc2corpus requires a spec, to be able to extract structured information from HTML pages. The spec is a Python dictionary containing two keys, `meta` (optional) and `extractors`.

### The `meta` entry (optional)

When running warc2corpus, the contents of the optional `meta` entry will be copied as-is into the result. This allows adding meta information to the result, such as the source of the information extracted, or the date of processing.

```python3
spec= {
  'meta': {
    'name': 'Uni Passau press releases',
    'location': 'WARCnet London 2022',
    'created_at': dt.now().isoformat()
  },
  'extracts': [
    # one or more extractors
  ]
}
```

### The `extracts` entry

The `extracts` entry contains a list of so-called _extractors_. Each extractor is itself a dictionary, containing the following keys: `name`, `css_path`, `f` (optional).

```python3
spec= {
  'extracts': [
    {
      'name': 'released_at',
      'css_path': '[itemprop~="datePublished"]',
      'f': lambda m: dp.parse(m[0]['datetime'].strip(), date_formats=['%d. %B %Y']).isoformat()
    }
  ]
}
```

 When running warc2corpus, each extractor will be applied on the HTML page processed. The `css_path` is used to select one or several elements from the HTML page. The information extracted will be stored under the key `released_at`, as defined by `name`. Instead of storing the date of release as-is, the lamba `f` is applied first, to transform the string `"14. Februar 1992"` into a datetime object.

### Results of Extraction

The result of applying the extractor above is the following JSON object. The `css_path` and the `name` have been copied into the result. The information extracted is stored under `value`, after applying the lambda `f` on it.

```json
[
  {
    "css_path": "header time",
    "name": "released_at",
    "value": "2022-02-14T17:04:21"
  }
]
```
