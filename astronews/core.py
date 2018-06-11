import asyncio
import re
import unicodedata
from collections import Counter
from pprint import pprint
from typing import Callable, Mapping, Sequence

from aiohttp import ClientSession
from bs4 import BeautifulSoup


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


def normalize_article(article: str) -> str:
    '''
    Transforma tudo em minúscula e remove diacríticos (acento, cedilha etc.),
    emojis e outras bizarrices unicode.
    '''
    return (unicodedata.normalize('NFKD', article.lower())
            .encode('ascii', 'ignore')
            .decode('ascii'))


def keyword_counter(keywords: Sequence[str]) \
        -> Callable[[str], Mapping[str, int]]:

    reg = re.compile(r'\b(?:{})\b'.format('|'.join(keywords)))

    def count_keywords(article):
        return Counter(reg.findall(article))

    return count_keywords


class NewsStoryCrawler:
    MAX_DEPTH = 3

    def __init__(self, session: ClientSession, keywords: Sequence[str]):
        self.keywords = keywords
        self.session = session
        self.visited = set()

    def get_story(self, parser: BeautifulSoup) -> str:
        raise NotImplementedError()

    def is_story(self, url: str) -> bool:
        raise NotImplementedError()

    def should_visit(self, url: str) -> bool:
        return True

    async def crawl(self, seed):
        counts = {}
        visited = set()
        count_kws = keyword_counter(self.keywords)

        q = asyncio.LifoQueue()
        await q.put((0, seed))

        while not q.empty():
            depth, url = await q.get()
            visited.add(url)
            print(url)

            content = await fetch(self.session, url)
            parser = BeautifulSoup(content, 'lxml')

            if self.is_story(url):
                counts[url] = count_kws(self.get_story(parser))
                pprint(counts[url])

            if depth < self.MAX_DEPTH:
                for link in parser.find_all('a', href=True):
                    href = link['href']
                    if href not in self.visited and self.should_visit(href):
                        await q.put((depth + 1, href))

        return counts

