**NOTE: this is a preview, things will change without warning.**

`warc2corpus` extracts text corpora from WARCs, according to a user-defined specification. The specification consists of CSS paths and (optional) transformations on the text extracted.

Requires AUT (Archivesunleashed Toolkit).

# Installation

Install AUT as described at their website and start a PySpark console.

See also `bin/pyspark`, your installation paths may vary.

# Example

First, an extractor must be defined. The extractor defined in `lib/warc2corpus/extractors/test.py` extracts the fields `title`, `body` and `released_at` from matching HTML pages found inside a WARC. HTML pages are matched by `netloc_regex` and `path_regex`.

Each extract defines a `css_path` to extract information. The optional `f` transforms the text extracted, for example to parse the date assigned to `released_at`.

```python
import re
import dateparser as dp
import datetime

extractors = [
    {
        'meta': {
            'name': 'Zeit, Mitteilung',
            'issuer': 'media_site',
            'platform': 'website',
            'type': 'article',
            'layout': 'a'
        },
        'netloc_regex': re.compile('www\.zeit\.de'),
        'path_regex': re.compile('^/news/.+$'),
        'extracts': [
            {
                'name': 'title',
                'css_path': 'title',
                'f': lambda m: m[0].get_text().strip().split('|')[0]
            },
            {
                'name': 'body',
                'css_path': 'div[class~="article-body"] p, div[class~="article-body"] li',
            },
            {
                'name': 'released_at',
                'css_path': 'time[class~="metadata__date"]',
                'f': lambda m: dp.parse(m[0].get_text(), date_formats=['%d. %B %Y']).isoformat()
            }
        ]
    }
]
```

Now, the extractor can be applied to a WARC.

```python
from aut import *
from pyspark.sql.functions import col, udf
from warc2corpus.text import extract
from warc2corpus.extractors import zeit_de, test, apply

df = WebArchive(sc, sqlContext, './data/sample.warc.gz').webpages().filter(col("url").like("%zeit.de/news%"))

# Create a UDF; the lambda invokes `apply`, passing the extractors to use.
extractor_udf = udf(lambda html: apply(html,test.extractors))
df2 = df.select(extractor_udf('content').alias('extract'))
df2.limit(1).collect()[0]['extract']
```
