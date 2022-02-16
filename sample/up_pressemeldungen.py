# docker run --rm -it --name aut -v $(pwd):/w2c --workdir=/w2c -e "PYTHONPATH=/w2c/lib" sepastian/aut:latest /spark/bin/pyspark --py-files /aut/target/aut.zip --jars /aut/target/aut-0.70.1-SNAPSHOT-fatjar.jar

from aut import *
from pyspark.sql.functions import col, udf
from pyspark.sql.types import MapType, StringType, ArrayType
from pyspark import SparkContext
from pyspark.sql import SQLContext
import warc2corpus as w2c
import re
import dateparser as dp
import json

sc = SparkContext.getOrCreate()
sqlContext = SQLContext(sc)

df1 = WebArchive(sc, sqlContext, './data/uni_passau_de_pressemeldungen.warc.gz')
df2 = df1.webpages().filter(col("url").rlike(".+/pressemeldungen/meldung/detail/[a-z]+"))

# https://stackoverflow.com/a/37428126/92049
def extract(config):
    #return udf(lambda html: json.dumps(w2c.apply(html,config)),ArrayType(MapType(StringType(),StringType())))
    return udf(lambda html: json.dumps(w2c.apply(html,config)))

config= [
    {
        'netloc_regex': re.compile('www\.zeit\.de'),
        'path_regex': re.compile('^/news/.+$'),
        'extracts': [
            {
                'name': 'title',
                'css_path': '.news .article header h1'
            },
            {
                'name': 'teaser',
                'css_path': '.teaser-text p'
            },
            {
                'name': 'body',
                'css_path': 'div[itemprop~="articleBody"] p'
            },
            {
                'name': 'author',
                'css_path': '[itemprop~="author"] [itemprop~="name"]'
            },
            {
                'name': 'released_at',
                'css_path': '[itemprop~="datePublished"]',
                'f': lambda m: dp.parse(m[0]['datetime'].strip(), date_formats=['%d. %B %Y']).isoformat()
            }
        ]
    }
]

df3 = df2.withColumn("extract", extract(config)(remove_http_header(col("content"))))

for r in df3.select("url","extract").collect():
    print(r.url, r.extract)
