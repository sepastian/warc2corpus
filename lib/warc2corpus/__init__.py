import bs4
from datetime import datetime as dt

def apply(content,extractors):
    """
    Apply extractors to content.
    """
    if not isinstance(extractors,(list,tuple)):
        extractors = [extractors]
    soup = bs4.BeautifulSoup(content,'lxml')
    result = []
    for extractor in extractors:
        meta = extractor.get('meta',{})
        meta['created_at'] = dt.now().isoformat()
        data = {}
        for e in extractor['extracts']:
            n = e.get('name','n/a')
            c = e.get('css_path',None)
            f = e.get('f',None)
            if not c:
                continue
            text = soup.select(c)
            if text and f:
                text = f(text)
            elif text:
                # Join all text rows,
                # if no lambda has been given,
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
    return result
