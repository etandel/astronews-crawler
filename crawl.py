# encoding: utf-8
from collections import Counter
import aiohttp
import asyncio
import re
import unicodedata
from pprint import pprint

from bs4 import BeautifulSoup
from typing import Callable, Mapping, Sequence


MAX_DEPTH = 3
KEY_WORDS = {'astron.+', 'astrof.+'}


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


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
    return 'g1.globo.com' in url


async def crawl_loop(session, seed, keywords):
    counts = {}
    visited = set()
    count_kws = keyword_counter(keywords)

    q = asyncio.LifoQueue()
    await q.put((0, seed))

    while not q.empty():
        depth, url = await q.get()
        visited.add(url)
        print(url)

        content = await fetch(session, url)
        parser = BeautifulSoup(content, 'lxml')

        if should_process(url):
            article = get_g1_article_normalized(parser)
            counts[url] = count_kws(article)
            pprint(counts[url])

        if depth < MAX_DEPTH:
            for link in parser.find_all('a'):
                href = link.get('href')
                if href and href not in visited and should_visit(href):
                    await q.put((depth + 1, href))
    return counts


async def main():
#    seed = 'http://g1.globo.com/ciencia-e-saude/'
    seed = 'https://g1.globo.com/bemestar/noticia/toxoplasmose-entenda-os-sintomas-e-como-se-prevenir.ghtml'

    async with aiohttp.ClientSession() as session:
        await crawl_loop(session, seed, KEY_WORDS)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

