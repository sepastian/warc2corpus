# docker run --rm -it --name aut -v $(pwd):/w2c --workdir=/w2c -e "PYTHONPATH=/w2c/lib" sepastian/aut:latest /spark/bin/pyspark --py-files /aut/target/aut.zip --jars /aut/target/aut-0.70.1-SNAPSHOT-fatjar.jar

from aut import *
from pyspark.sql.functions import col, udf
from warc2corpus.text import extract
from warc2corpus.extractors import zeit_de, test, apply

df = WebArchive(sc, sqlContext, './data/sample.warc.gz').webpages().filter(col("url").like("%zeit.de/news%"))
extractor_udf = udf(lambda html: apply(html,test.extractors))
df2 = df.select(extractor_udf('content').alias('extract'))
df2.limit(1).collect()[0]['extract']

#df.select(extract('content',zeit_de))
