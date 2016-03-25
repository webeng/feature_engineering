from bs4 import BeautifulSoup
import re
from urlparse import urlparse


class AuthorExtractor(object):

	@classmethod
	def clean_author(self, href, text=None):
		author = None
		if text:
			return text
		else:
			for part in href.split('/')[::-1]:
				if part not in ['', '/']:
					author = part.capitalize().replace('-', ' ')
					break

		return author

	@classmethod
	def extract(self, base_url, html):
		authors = []
		soup = BeautifulSoup(html, 'html.parser')

		for a in soup.findAll('a'):
			href = a.get('href')

			if href:
				if re.search('.author.?/.', href) is not None:
					authors.append(self.clean_author(href, a.get_text()))
				elif re.search('.people/.', href) is not None:
					authors.append(self.clean_author(href, a.get_text()))
				elif (re.search('.user.?/.', href) is not None) & (re.search('.youtube.com.', href) is None):
					authors.append(self.clean_author(href, a.get_text()))
				elif re.search('.editor.?/.', href) is not None:
					authors.append(self.clean_author(href, a.get_text()))
				elif re.search('.contributor.?/.', href) is not None:
					authors.append(self.clean_author(href, a.get_text()))

		if not authors:
			author = None
			url_parse = urlparse(base_url)
			domain = url_parse.netloc.split('.')
			if len(domain) >= 2:
				author = domain[1] if domain[0] == 'www' else domain[0]

			authors.append(author.capitalize() + ' Staff')

		return authors

if __name__ == '__main__':
	from goose import Goose
	aE = AuthorExtractor()
	target_url = 'http://www.wired.com/2016/03/1000-days-1000-surreal-posters-one-unfortunate-design/'
	article = Goose().extract(target_url)
	print aE.extract(target_url, article.raw_html)
