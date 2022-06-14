# docker run --rm -it --name aut -v $(pwd):/w2c --workdir=/w2c -e "PYTHONPATH=/w2c/lib" sepastian/aut:latest /spark/bin/pyspark --py-files /aut/target/aut.zip --jars /aut/target/aut-0.70.1-SNAPSHOT-fatjar.jar

import json
import dateparser as dp
from datetime import datetime as dt
from pathlib import Path
from warc2corpus import run

# Find the WARC archive file to process.
#
# When running the sample-spark make target,
# the data/ directory of this repository
# will be mounted at /w2c/data inside the container.
base = Path(__file__).parent.parent
data_dir = base.joinpath('data')
warc_file = data_dir.joinpath("uni_passau_de_pressemeldungen_20220216T125953.warc")

# Supply a regex selecting pages to process by URL.
url_regex = ".+/pressemeldungen/meldung/detail/[a-z]+"

# Configure warc2corpus.
#
# The following configuration will be applied to each web page selected above.
# Pages will be processed one by one.
#
# During processing, a result in JSON format will be generated.
#
# The 'meta' information will be copied to the JSON result as-is.
# It contains arbitrary information as key-value pairs.
#
# Each 'exctract' defines a piece of information to extract from the page
# currently processed. An exctract defines:
#
#   * the 'name' under wich to store the information extracted;
#   * the 'css_path' at which to find the information within the web page;
#   * an optional function 'f' to transform the data extracted
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

# Run warc2corpus, supplying the URL pattern and configuration defined above.
# This will return a (Py)Spark data frame.
df = run(warc_file, config, url_regex=url_regex)

# Write the results to a file in JSON format.
out_dir = data_dir.joinpath('sample_run_{}'.format(dt.now().strftime('%Y%m%dT%H%M%S')))
print(f'Writting results to #{out_dir}.')
df.write.json(str(out_dir))
