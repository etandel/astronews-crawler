# encoding: utf-8
import asyncio
import sys

import aiohttp
from bs4 import BeautifulSoup

from astronews.core import NewsStoryCrawler


class G1Crawler(NewsStoryCrawler):
    DEFAULT_SEED = 'https://g1.globo.com/bemestar/noticia/toxoplasmose-entenda-os-sintomas-e-como-se-prevenir.ghtml'

    def get_story(self, parser: BeautifulSoup) -> str:
        return parser.find('article')

    def is_story(self, url: str) -> bool:
        return '/noticia/' in url

    def should_visit(self, url: str) -> bool:
        return 'g1.globo.com' in url


async def main():
#    seed = 'http://g1.globo.com/ciencia-e-saude/'
    seed = 'https://g1.globo.com/bemestar/noticia/toxoplasmose-entenda-os-sintomas-e-como-se-prevenir.ghtml'

CRAWLERS = {
    'g1': G1Crawler,
}


async def main():
    crawler_code = sys.argv[1]
    async with aiohttp.ClientSession() as session:
        crawler = CRAWLERS[crawler_code](session, {'astron.+', 'astrof.+'})
        await crawler.crawl()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

