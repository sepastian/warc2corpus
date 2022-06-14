import bs4
from datetime import datetime as dt
from aut import *
from pyspark.sql.functions import col, udf, from_json, explode, concat
from pyspark.sql.types import * #MapType, StringType, ArrayType, StructType, from_json
from pyspark import SparkContext
from pyspark.sql import SQLContext
from json import dumps

def run(warc_file, config, url_regex='.*'):
    """
    Main entry point for warc2corpus.
    """
    sc = SparkContext.getOrCreate()
    sqlContext = SQLContext(sc)
    df1 = WebArchive(sc, sqlContext, str(warc_file))
    df2 = df1.all().filter(col("url").rlike(url_regex))
    df3 = df2.withColumn("extract", extract(config)(remove_http_header(col("raw_content"))))
    df4 = df3.select(df3.url, from_json('extract','ARRAY<MAP<STRING,STRING>>').alias('extract'))
    return df4

# https://stackoverflow.com/a/37428126/92049
def extract(config):
    """
    Generate a Spark UDF.

    This encloses warc2corpus' apply function to make
    the configuration available to Spark during processing.
    """
    return udf(lambda html: dumps(apply(html,config)))

def apply(content, extractors):
    """
    Apply extractors to content.
    """
    if not isinstance(extractors,(list,tuple)):
        extractors = [extractors]
    soup = bs4.BeautifulSoup(content,'lxml')
    result = []
    for extractor in extractors:
        meta = { 'created_at': dt.now().isoformat() }
        if 'meta' in extractor:
            meta = extractor['meta']
        result.append(meta)
        for e in extractor['extracts']:
            n = e.get('name','n/a')
            c = e.get('css_path',None)
            f = e.get('f',None)
            if not c:
                continue
            data = {
                'name': n,
                'css_path': c
            }
            text = soup.select(c)
            if text and f:
                text = f(text)
            elif text:
                # Join all text rows,
                # if no lambda has been given,
                text = ' '.join([ m.get_text().strip() for m in text ])
            data['value']= text or None
            # Check, if extracted data is valid, store under 'meta.valid';
            # the extractor may specify a callable under 'validator';
            # if 'validator' exists, insert its return value under 'meta.valid';
            # if it does not exist, check, if all extracted values are non-empty.
            # if not 'validator' in extractor:
            #     # (not not on an empty string returns False.)
            #     extractor['validator'] = lambda pairs: all([ not not v for k,v in pairs ])
            #     #pairs = list(((k,v['value']) for k,v in data.items()))
            #     meta['valid'] = extractor['validator'](pairs)
            result.append(data)
        #result.append({'meta':meta,'data':data})
    return result
