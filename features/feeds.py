import re
import requests
from bs4 import BeautifulSoup
from urlparse import urlparse


class FeedsExtractor(object):

	@classmethod
	def extract(self, url):
		rss = []
		headers = {'Accept': ':text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
				   'Accept-Encoding': 'gzip,deflate,sdch',
				   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36'}

		r = requests.get(url, headers=headers)
		soup = BeautifulSoup(r.text, "html.parser")

		for a in soup.find_all(['a', 'link']):
			href = a.get('href')
			# find urls that contain .rss
			if href:
				if 'rss' in href:
					rss.append(href)
				elif '/feed' in href:
					rss.append(href)

		if not rss:
			feep_paths = ['feed', 'rss']
			o = urlparse(url)
			clean_url = o.scheme + "://" + o.netloc

			for f in feep_paths:
				try_url = clean_url + "/" + f
				r = requests.get(try_url, headers=headers)
				if r.status_code == 200:
					rss.append(try_url)

		return self._clean_rss(rss, url)

	@classmethod
	def _clean_rss(self, rss, base_url):
		o_base = urlparse(base_url)
		for i, item in enumerate(rss):
			o = urlparse(item)
			scheme = o.scheme
			netloc = o.netloc
			if not o.scheme:
				scheme = o_base.scheme
			if not o.netloc:
				netloc = o_base.netloc

			rss[i] = scheme + "://" + netloc + o.path

		return list(set(rss))

if __name__ == '__main__':
	fE = FeedsExtractor()
	print ext_rss.extract('http://techcrunch.com')
