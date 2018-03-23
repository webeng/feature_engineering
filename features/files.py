# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urlparse import urlparse
import re


class FilesExtractor(object):

	@classmethod
	def extract(cls, base_url, html):

		soup = BeautifulSoup(html, 'html.parser')
		pattern = re.compile('.*\.pdf|.*\.xls')
		base_url_parsed_netloc = urlparse(base_url).netloc.replace('www.', '')
		file_urls, context_text = [], []

		for a in soup.find_all('a'):
			try:
				a_netloc = urlparse(a['href']).netloc.replace('www.', '')
				if a_netloc == base_url_parsed_netloc:

					a_title = a['title']
					a_text = a.getText()
					matches = re.finditer(pattern, a['href'])

					for m in matches:

						# Seek context text
						txt = []
						if a_title:
							txt.append(a_title)
						if a_text:
							txt.append(a_text)

						file_urls.append(a['href'])
						context_text.append(" ".join(txt))

			except KeyError, e:
				continue

		return file_urls, context_text

if __name__ == '__main__':
	from goose import Goose
	fE = FilesExtractor()
	# target_url = 'https://traditionalbrickandstone.co.uk/product/victoria-falls/'
	target_url = 'http://www.imperialhandmadebricks.co.uk/products/yellow-stock/'
	article = Goose().extract(target_url)
	print fE.extract(target_url, article.raw_html)
