# -*- coding: utf-8 -*-
import hashlib
import requests
from features.main_text import MainTextExtractor
from lxml import html
import pprint
import re
from features.file2text import File2Text


class Url2Text(object):

    @classmethod
    def extract(cls, url, content_type=None):
        texts = []
        file2text = File2Text()

        pdf_pattern = re.compile('.*application\/pdf.*|.*application\/octet-stream.*')
        html_pattern = re.compile('.*text\/html.*')

        try:
            r = requests.get(url, timeout=30)
        except requests.exceptions.SSLError, e:
            r = requests.get(url, verify=False)

        if not content_type:
            content_type = r.headers['Content-Type']

        print content_type

        matches_html = len(re.findall(html_pattern, content_type))
        matches_pdf = len(re.findall(pdf_pattern, content_type))

        if r.status_code == 200:
            if matches_html == 0:

                file_prefix = hashlib.md5(url).hexdigest()

                dst_path = './tmp/'

                dst = dst_path + file_prefix + '_' + url.split('/')[-1]

                with open(dst, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                # call PDF2Text
                texts = [file2text.extract_all(dst)]
            else:
                texts = filter(None, MainTextExtractor.extract(r.text, html.fromstring(r.text)))

        return texts

if __name__ == '__main__':
    # this packages should be here but we only need the for improving the
    # extractor therefore it might interfere with the rest of the project
    url2text = Url2Text()
    # PDF
    # target_url = "https://ocs.fas.harvard.edu/files/ocs/files/undergrad_resumes_and_cover_letters.pdf"
    target_url = 'http://www.artisansofdevizes.com/product-collections/standard-tiles-flagstones/waldorf-limestone-collection-papyrus/'
    # Image
    target_url = 'https://onepagelove-wpengine.netdna-ssl.com/wp-content/uploads/2016/10/opl-small-1.jpg'
    # Mp3 if it returns  and error - Run brew install sox  or sudo apt-get install sox
    target_url = 'http://www.noiseaddicts.com/samples_1w72b820/47.mp3'
    # article = Goose().extract(target_url)
    texts = url2text.extract(target_url)
    print texts
    # print tE.extract(article.raw_html, article.raw_doc)