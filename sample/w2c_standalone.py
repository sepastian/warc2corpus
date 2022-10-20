# make console
# /spark/bin/spark-submit \
#   --py-files /aut/target/aut.zip \
#   --jars=/aut/target/aut-0.91.1-SNAPSHOT-fatjar.jar \
# sample/sample.py

from pathlib import Path
import re
import json
import dateparser as dp
import warc2corpus as w2c

base= Path(__file__).parent.parent
datadir= base.joinpath('data')
samplefile= datadir.joinpath('sueddeutsche_artikel_20220208.html')
html= open(samplefile,'r',encoding='utf-8').read()

spec= {
    'meta': {
        'name': 'Sueddeutsche Artikel',
        'issuer': 'media_site',
        'platform': 'website',
        'type': 'article',
        'layout': 'a'
    },
    'extracts': [
        {
            'name': 'title',
            'css_path': 'article header h2',
            'f': lambda m: m[0].get_text().strip().split('|')[0]
        },
        {
            'name': 'body',
            'css_path': 'div[itemprop~="articleBody"] p',
        },
        {
            'name': 'author',
            'css_path': 'article > p:first-of-type',
            'f': lambda m: re.sub('^Von ', '', m[0].get_text())
        },
        {
            'name': 'released_at',
            'css_path': 'header time',
            'f': lambda m: dp.parse(m[0]['datetime'].strip(), date_formats=['%d. %B %Y']).isoformat()
        }
    ]
}

result= w2c.apply(html, spec)

print(json.dumps(result,indent=4,sort_keys=True))
