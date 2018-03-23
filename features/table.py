# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from goose import Goose


class TableExtractor(object):

    @classmethod
    def _get_tables(cls, html):
        """
        Method to extract tables from html
        """

        soup = BeautifulSoup(html, 'html.parser')
        return [t for t in soup.find_all('table')]

    @classmethod
    def extract(cls, html, page_html):

        soup = BeautifulSoup(html, 'html.parser')
        tables = []
        excluded_tags = [
            'script', 'style', 'noscript', 'head', 'meta',
            'header', 'footer', 'link', 'input', 'nav'
        ]

        [x.extract() for et in excluded_tags for x in soup.find_all(et) if x]

        for t in soup.find_all('table'):
            tables.append(t)

        return tables

if __name__ == '__main__':
    # this packages should be here but we only need the for improving the
    # extractor therefore it might interfere with the rest of the project
    tE = TableExtractor()
    target_url = 'http://www.artisansofdevizes.com/product-collections/standard-tiles-flagstones/waldorf-limestone-collection-papyrus/'
    article = Goose().extract(target_url)
    print tE.extract(article.raw_html, article.raw_doc)