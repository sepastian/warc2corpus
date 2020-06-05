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
