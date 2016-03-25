from features.title import TitleExtractor
from features.main_text import MainTextExtractor
from features.images import ImagesExtractor
from features.sentiment import getSentimentText, findSentiment
from features.keywords import KeywordsExtractor
from features.keywords import KeywordsExtractor
from features.entities import Entities
from features.author import AuthorExtractor
from features.category import Classifier
from goose import Goose
from lxml import etree
from pyteaser_c import Summarize
from pyteaser_c import SummarizePage
from pyteaser_c import GetArticle
from pyteaser_c import keywords
from textblob import TextBlob
import langid


class Link(object):
	@classmethod
	def extract(self, link, entity_description=False, sentiment=False):
		errors, summaries, categories, entities, keywords = [], [], [], [], []
		article = Goose().extract(link)
		authors = AuthorExtractor.extract(link, article.raw_html)

		publish_date = article.publish_date if article.publish_date else None

		if not article.title:
			article.title = TitleExtractor.extract(
				article.raw_html, article.raw_doc)[0]

		k = KeywordsExtractor(num_kewyords=20, verbose=True)

		if article.top_node:
			main_body = etree.tostring(article.top_node)
		else:
			article.cleaned_text = MainTextExtractor.extract(
				article.raw_html, article.raw_doc)[1]
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
			clf = Classifier()
			article.categories = clf.predict(text)
		else:
			article.categories = ["Article classification not ready for: " + language[0]]

		if article.top_image:
			thumbnail = article.top_image.src
		else:
			images = ImagesExtractor.extract(link, article.raw_html)
			if images:
				thumbnail = images[0]

		return {
			"title": article.title,
			"link": article.final_url,
			"author": authors,
			"cleaned_text": article.cleaned_text,
			"text_sentiment": text_sentiment,
			"main_body": main_body,
			"image": thumbnail,
			"date": article.publish_date,
			"tags": keywords,
			"entities": entities,
			"language": language,
			"summary": summaries,
			"categories": article.categories
		}

if __name__ == '__main__':
	l = Link()
	l = l.extract('http://techcrunch.com/2016/03/18/twitter-says-few-users-have-opted-out-of-its-new-algorithmic-timeline/')
	print l
