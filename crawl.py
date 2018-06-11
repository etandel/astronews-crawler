# encoding: utf-8
from collections import Counter
from queue import LifoQueue
import re
import requests
import unicodedata
from pprint import pprint

from bs4 import BeautifulSoup
from typing import Callable, Mapping, Sequence


MAX_DEPTH = 3
KEY_WORDS = {'astron.+', 'astrof.+'}


def normalize(article: str) -> str:
    '''
    Transforma tudo em minúscula e remove diacríticos (acento, cedilha etc.),
    emojis e outras bizarrices unicode.
    '''
    return (unicodedata.normalize('NFKD', article.lower())
            .encode('ascii', 'ignore')
            .decode('ascii'))


def get_g1_article_normalized(parser: BeautifulSoup) -> str:
    article = parser.find('article')
    return normalize(article.text) if article else ''


def keyword_counter(keywords: Sequence[str]) \
        -> Callable[[str], Mapping[str, int]]:

    reg = re.compile(r'\b(?:{})\b'.format('|'.join(keywords)))

    def count_keywords(article):
        return Counter(reg.findall(article))

    return count_keywords


def should_process(url):
    return '/noticia/' in url


def should_visit(url):
    return 'g1.globo.com' in href


if __name__ == '__main__':
    counts = {}

    q = LifoQueue()
    visited = set()
    count_kws = keyword_counter(KEY_WORDS)

#    seed = 'http://g1.globo.com/ciencia-e-saude/'
    seed = 'https://g1.globo.com/bemestar/noticia/toxoplasmose-entenda-os-sintomas-e-como-se-prevenir.ghtml'
    q.put((0, seed))
    while not q.empty():
        depth, url = q.get()
        visited.add(url)
        print(url)

        r = requests.get(url)
        try:
            r.raise_for_status()
        except Exception:
            pass
        else:
            parser = BeautifulSoup(r.content, 'lxml')

            if should_process(url):
                article = get_g1_article_normalized(parser)
                counts[url] = count_kws(article)
                pprint(counts[url])

            if depth < MAX_DEPTH:
                for link in parser.find_all('a'):
                    href = link.get('href')
                    if href and href not in visited and should_visit(href):
                        q.put((depth + 1, href))

