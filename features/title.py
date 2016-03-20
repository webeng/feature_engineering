# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from goose import Goose
from goose.article import Article
from goose.extractors.title import TitleExtractor as TitleExtractorGoose
from goose.configuration import Configuration


class TitleExtractor(object):

    SPLIT_CHARS = ['|', '–', '-']

    def __init__(self):
        pass

    @classmethod
    def extract_text(cls, tag):
        if tag.string:
            return tag.string.strip().encode('utf-8', 'replace')
        return None

    @classmethod
    def extract(cls, html, html_formated):

        potential_titles = []
        soup = BeautifulSoup(html, 'html.parser')

        if soup.title:
            page_title = TitleExtractor.extract_text(soup.title)

            for split_char in TitleExtractor.SPLIT_CHARS:
                if split_char in page_title:
                    page_title = page_title.split(split_char)[0].strip()

            potential_titles.append(page_title)

        for heading_tag in (soup.find_all('h1') + soup.find_all('h2')):
            potential_title = TitleExtractor.extract_text(heading_tag)
            if potential_title:
                potential_titles.append(potential_title)

        # Extract article from goose
        article = Article()
        article.raw_html = html
        article.raw_doc = html_formated
        article.doc = article.raw_doc
        goose_title = TitleExtractorGoose(Configuration(), article).get_title()

        return list(set(potential_titles + [goose_title]))

if __name__ == '__main__':

    tE = TitleExtractor()
    target_url = 'http://www.toshiba-aircon.co.uk/products/refrigerant-leak-detection-solutions/refrigerant-leak-detection-solutions/rbc-aip4'
    article = Goose().extract(target_url)
    print tE.extract(article.raw_html, article.raw_doc)
