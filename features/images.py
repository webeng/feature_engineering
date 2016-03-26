# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urlparse import urlparse
import urllib
import cStringIO
from PIL import Image


class ImagesExtractor(object):

	@classmethod
	def _normalise_url(cls, base_url, url):
		"""
		Normalises a relative url to an absolute one if base domain is not
		present.
		"""
		parsed_url = urlparse(url)

		if not parsed_url.netloc:
			return base_url + '/'.join([segment
							 for segment in parsed_url.path.split('/')
							 if segment not in ['..', '.', '', None]]) + '?' + parsed_url.query
		elif not parsed_url.scheme:
			return 'http:' + url

		return url

	@classmethod
	def _process_image(cls, base_url, img_url):
		return ImagesExtractor._normalise_url(base_url, img_url)

	@classmethod
	def _get_zoom_image(cls, img):
		if img.parent.get('href'):
			return img.parent.get('href')
		else: # if not href, try data attributes
			for key, value in img.parent.attrs.iteritems():
				if key.startswith('data-'):
					if value.startswith('http://'):
						return value
		return None

	@classmethod
	def _get_meta_image(cls, meta_tag):
		return meta_tag.get('content')

	@classmethod
	def select_top_image(cls, images):
		max_surface = 0
		selected = None
		for img_src in images:
			file = cStringIO.StringIO(urllib.urlopen(img_src).read())
			try:
				im = Image.open(file)
			except IOError, e:
				continue
			width, height = im.size
			if width > 100 and height > 100:
				surface = (width * height) / 2
				if surface > max_surface:
					selected = img_src
					max_surface = surface

		return selected

	@classmethod
	def extract(cls, base_url, html):
		soup = BeautifulSoup(html, 'html.parser')

		img_tag_urls = filter(None, [img.get('src') for img in soup.find_all('img')])
		zoom_img_urls = filter(None, [ImagesExtractor._get_zoom_image(img) for img in soup.select('a > img')])
		meta_img_urls = filter(None, [ImagesExtractor._get_meta_image(mtag) for mtag in soup.select('meta[property=og:image]')])
		image_urls = img_tag_urls + zoom_img_urls + meta_img_urls

		return [ImagesExtractor._process_image(base_url, image_url) for image_url in image_urls]

if __name__ == '__main__':
	from goose import Goose
	iE = ImagesExtractor()
	target_url = 'http://www.toshiba-aircon.co.uk/products/refrigerant-leak-detection-solutions/refrigerant-leak-detection-solutions/rbc-aip4'
	article = Goose().extract(target_url)
	print iE.extract(target_url, article.raw_html)
