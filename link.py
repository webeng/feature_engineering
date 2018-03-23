from features.title import TitleExtractor
from features.main_text import MainTextExtractor
from features.images import ImagesExtractor
from features.sentiment import getSentimentText, findSentiment
from features.keywords import KeywordsExtractor
from features.entities import Entities
from features.author import AuthorExtractor
from features.category import Classifier
from features.url2text import Url2Text
from goose import Goose
from lxml import etree
from pyteaser_c import Summarize
from pyteaser_c import SummarizePage
from pyteaser_c import GetArticle
from pyteaser_c import keywords
from textblob import TextBlob
import langid
from bs4 import BeautifulSoup
#import lxml.html
from lxml import html
import requests
import pprint
import re
import os


class NoMainTextException(Exception):
    pass


class Link(object):
	# def is_html(self):
	# 	pass

	@classmethod
	def extract(self, link, entity_description=False, sentiment=False, data_path='./data/'):
		errors, summaries, categories, entities, keywords = [], [], [], [], []
		pdf_pattern = re.compile('.*application\/pdf.*|.*application\/octet-stream.*')
		html_pattern = re.compile('.*text\/html.*')

		article = Goose().extract(link)

		content_type = article.__dict__['additional_data']['result'].info()['content-type']
		matches_html = len(re.findall(html_pattern, content_type))
		matches_pdf = len(re.findall(pdf_pattern, content_type))

		if matches_html == 0:
			# Textract
			url2text = Url2Text()
			texts = url2text.extract(link)

			k = KeywordsExtractor(num_kewyords=20, verbose=True, data_path=data_path)
			ent = Entities()
			clf = Classifier(data_path=data_path)

			return {
				"title": os.path.basename(link),
				"link": link,
				"author": [],
				"cleaned_text": texts[0],
				"text_sentiment": getSentimentText(texts[0]),
				"main_body": None,
				"images": None,
				"image": None,
				"date": article.__dict__['additional_data']['result'].info()['last-modified'],
				"tags": k.extract([texts[0]], None, None, 'news')[0],
				"entities": ent.extract(texts[0], entity_description),
				"language": langid.classify(texts[0])[0],
				"summary": Summarize(None, texts[0]),
				"categories": clf.predict(texts[0])
			}
			pass
		else:

			valid_html = bool(BeautifulSoup(article.raw_html[0:100], "html.parser").find())

			if not valid_html:
				headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'}
				r = requests.get(link, headers=headers)
				article.raw_html = r.text
				article.raw_doc = html.fromstring(r.text)

			if article.raw_doc is None:
				raise NoMainTextException

			authors = AuthorExtractor.extract(link, article.raw_html)
			publish_date = article.publish_date if article.publish_date else None

			if not article.title:
				article.title = TitleExtractor.extract(
					article.raw_html, article.raw_doc)[0]

			k = KeywordsExtractor(num_kewyords=20, verbose=True, data_path=data_path)

			if article.top_node is not None:
				main_body = etree.tostring(article.top_node)
			else:
				cleant_text_suggestions = MainTextExtractor.extract(article.raw_html, article.raw_doc)
				article.cleaned_text = cleant_text_suggestions[1]
				if not article.cleaned_text:
					article.cleaned_text = cleant_text_suggestions[2]
				if not article.cleaned_text:
					raise NoMainTextException
				main_body = 'Sorry, we could not detect the main HTML content for this article'

			try:
				summaries = Summarize(
					article.title, article.cleaned_text.encode('utf-8', 'ignore'))
			except Exception, e:
				summaries.append('We could not make summaries at this time.')

			try:
				text_sentiment = getSentimentText(article.cleaned_text)
			except Exception, e:
				text_sentiment = None
			text = article.title + " " + article.cleaned_text
			keywords = k.extract([text], None, None, 'news')[0]

			# Get keywords from meta tag
			if not keywords:
				keywords = article.meta_keywords.split(',')

			# Get keywords from Goose
			if not keywords:
				keywords = [t for t in article.tags]

			if sentiment:
				keywords = findSentiment(keywords)

			ent = Entities()
			try:
				entities = ent.extract(text, entity_description)
			except Exception, e:
				entities.append('We could not extract entities at this time.')

			if sentiment:
				entities = findSentiment(entities)

			language = article.meta_lang

			if not language:
				language = langid.classify(article.cleaned_text)[0]

			if language in ['en', 'eo']:
				clf = Classifier(data_path=data_path)
				article.categories = clf.predict(text)
			else:
				article.categories = ["Article classification not ready for: " + language[0]]

			images = ImagesExtractor.extract(link, article.raw_html)

			if article.top_image:
				thumbnail = article.top_image.src
			else:
				#thumbnail = images[0] if images else None
				thumbnail = ImagesExtractor.select_top_image(images[0:50])

			return {
				"title": article.title,
				"link": article.final_url,
				"author": authors,
				"cleaned_text": article.cleaned_text,
				"text_sentiment": text_sentiment,
				"main_body": main_body,
				"images": images,
				"image": thumbnail,
				"date": article.publish_date,
				"tags": keywords,
				"entities": entities,
				"language": language,
				"summary": summaries,
				"categories": article.categories
			}

if __name__ == '__main__':
	import pprint
	l = Link()
	url = 'https://www.wired.com/2017/05/google-just-made-email-heckuva-lot-easier-deal/'
	# l = l.extract('http://techcrunch.com/2016/03/18/twitter-says-few-users-have-opted-out-of-its-new-algorithmic-timeline/')
	#l = l.extract('https://www.wired.com/2017/05/google-just-made-email-heckuva-lot-easier-deal/')
	# l = l.extract('http://www.independent.co.uk/life-style/gadgets-and-tech/features/google-lens-ai-preview-features-so-impressive-its-scary-a7745686.html')
	# l = l.extract('https://onepagelove-wpengine.netdna-ssl.com/wp-content/uploads/2016/10/opl-small-1.jpg')
	target_url = 'http://www.noiseaddicts.com/samples_1w72b820/47.mp3'
	l = l.extract(target_url)

	pprint.pprint(l)
	# import requests 
	# r = requests.get(url)
	# print r.text
