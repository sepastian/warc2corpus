import os
import sys
import re
import pkgutil
import importlib
import traceback
from jsonschema import validate, ValidationError
import bs4
import datetime
import json

# Create a list of extractors from module in `pwd`.
# Each extractor is a dictionary, containing the keys:
#
#   * netloc_regex
#   * path_regex
#   * extracts
#
# Both `netloc_regex` and `path_regex` are regular expressions,
# used for selecting an extractor based on host and path.
# After selecting an extractor, all elements of the list `extracts`
# are applied to the HTML of that page; each elements contains the keys
#
#   * `name`
#   * `css_path`
#   * `f`
#
# The result of applying an extract is stored under the key `name`;
# elements are selected using the CSS path found at `css_path`;
# the actual value is obtained applying `f` to the elements extracted by
# CSS path.
schema = {
    "type": "object",
    "properties": {
        "meta": {
            "type": "object",
            "properties": {
                "name": { "type": "string" },
                "issuer": {
                    "type": "string",
                    "enum": ["political_party", "politician", "media_site"]
                },
                "platform": {
                    "type": "string",
                    "enum": ["website","social_media"]
                },
                "layout": {
                    "type": "string",
                    "pattern": "[a-z]+"
                },
                "type": {
                    "type": "string",
                    "enum": ["article","page"]
                }
            },
            "required": [
                "issuer", "platform", "layout", "type"
            ]
        },
    },
}
extractors = []
for (_, name, _) in pkgutil.iter_modules([os.path.dirname(__file__)]):
    # Relative import.
    m = importlib.import_module('.' + name, package='warc2corpus.extractors')
    # Augment meta info with name of extractor module.
    for e in m.extractors:
        try:
            validate(instance=e,schema=schema)
        except ValidationError as err:
            raise ValidationError("Error validating JSON schema for extractor {}.".format(name)) from err
        e['meta']['extractor'] = 'extractors.{}'.format(name)
        # Let 'f' default to lambda s: True'.
        e['f'] = e.get('f',lambda s: True)
        # Let 'query_regex' default to '.*'.
        e['query_regex'] = e.get('query_regex',re.compile('.*'))
    extractors += m.extractors

def apply(content,extractors):
    """
    Apply extractor to content.
    """
    soup = bs4.BeautifulSoup(content,'lxml')
    result = []
    for extractor in extractors:
        # Meta information about extraction.
        meta = extractor.get('meta',{})
        meta['created_at'] = datetime.datetime.now().isoformat()
        data = {}
        for e in extractor['extracts']:
            n = e.get('name','n/a')
            c = e.get('css_path',None)
            f = e.get('f',None)
            if not c:
                continue
            text = soup.select(c)
            if text and f:
                #log.debug(text)
                text = f(text)
            elif text:
                # If no lambda has been given,
                # join all text rows.
                text = ' '.join([ m.get_text().strip() for m in text ])
            data[n] = {
                'css_path': c,
                'value': (text or None)
            }
            # Check, if extracted data is valid, store under 'meta.valid';
            # the extractor may specify a callable under 'validator';
            # if 'validator' exists, insert its return value under 'meta.valid';
            # if it does not exist, check, if all extracted values are non-empty.
            if not 'validator' in extractor:
                # (not not on an empty string returns False.)
                extractor['validator'] = lambda pairs: all([ not not v for k,v in pairs ])
                pairs = list(((k,v['value']) for k,v in data.items()))
                meta['valid'] = extractor['validator'](pairs)
            result.append({'meta':meta,'data':data})
        return json.dumps(result)
