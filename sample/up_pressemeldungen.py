# docker run --rm -it --name aut -v $(pwd):/w2c --workdir=/w2c -e "PYTHONPATH=/w2c/lib" sepastian/aut:latest /spark/bin/pyspark --py-files /aut/target/aut.zip --jars /aut/target/aut-0.70.1-SNAPSHOT-fatjar.jar

from aut import *
from pyspark.sql.functions import col, udf, from_json, explode, concat
from pyspark.sql.types import * #MapType, StringType, ArrayType, StructType, from_json
from pyspark import SparkContext
from pyspark.sql import SQLContext
import warc2corpus as w2c
import re
import dateparser as dp
import json
from datetime import datetime as dt
from pathlib import Path

sc = SparkContext.getOrCreate()
sqlContext = SQLContext(sc)

warcfile = "uni_passau_de_pressemeldungen_20220216T125953.warc"
df1 = WebArchive(sc, sqlContext, './data/uni_passau_de_pressemeldungen_20220216T125953.warc.gz')
#df2 = df1.webpages().filter(col("url").rlike(".+/pressemeldungen/meldung/detail/[a-z]+"))
df2 = df1.all().filter(col("url").rlike(".+/pressemeldungen/meldung/detail/[a-z]+"))

# https://stackoverflow.com/a/37428126/92049
def extract(config):
    #return udf(lambda html: json.dumps(w2c.apply(html,config)),ArrayType(MapType(StringType(),StringType())))
    #return udf(lambda html: json.dumps(w2c.apply(html,config)))
    #schema = MapType(StringType(),StructType(),False)
    #schema.add('meta',StringType(),False)
    return udf(lambda html: json.dumps(w2c.apply(html,config)))

config= [
    {
        'meta': {
            'name': 'Uni Passau press releases',
            'location': 'WARCnet London 2022',
            'created_at': dt.now().isoformat()
        },
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

df3 = df2.withColumn("extract", extract(config)(remove_http_header(col("raw_content"))))

for r in df3.select("url","extract").collect():
    #j = json.loads(r.extract)
    print(r.extract)
    print(type(r.extract))
    #data.append(j[c] for doc in j for c in columns)

#df3.select("url","extract").write.json("data/test")

df4 = df3.select(df3.url, from_json('extract','ARRAY<MAP<STRING,STRING>>').alias('extract'))

#df5 = df4.select(df4.url, explode(df4.json).alias('data'))
df5 = df4

for r in df5.collect():
    print(r.extract)
    print(type(r.extract))
#df4.select("url","json").write.json("data/test")

#df5 = df4.select(df4.json.meta.alias('meta'))
#df5.show(vertical=True)

base = Path(__file__).parent.parent
data_dir = base.joinpath('data')
out_dir = data_dir.joinpath('sample_run_{}'.format(dt.now().strftime('%Y%m%dT%H%M%S')))
print(f'Writting results to #{out_dir}.')
df5.write.json(str(out_dir))
