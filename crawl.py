# encoding: utf-8
import asyncio

import aiohttp
from bs4 import BeautifulSoup

from astronews.core import NewsStoryCrawler, normalize_article


class G1Crawler(NewsStoryCrawler):
    def get_story(self, parser: BeautifulSoup) -> str:
        article = parser.find('article')
        return normalize_article(article.text) if article else ''

    def is_story(self, url: str) -> bool:
        return '/noticia/' in url

    def should_visit(self, url: str) -> bool:
        return 'g1.globo.com' in url


async def main():
#    seed = 'http://g1.globo.com/ciencia-e-saude/'
    seed = 'https://g1.globo.com/bemestar/noticia/toxoplasmose-entenda-os-sintomas-e-como-se-prevenir.ghtml'

    async with aiohttp.ClientSession() as session:
        crawler = G1Crawler(session, {'astron.+', 'astrof.+'})
        await crawler.crawl(seed)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

