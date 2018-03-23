# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup, Comment
from sklearn import preprocessing
import numpy as np
from goose import Goose
from goose.article import Article
from goose.configuration import Configuration
from goose.cleaners import DocumentCleaner
from goose.extractors.content import ContentExtractor
from goose.extractors.images import ImageExtractor
from goose.outputformatters import OutputFormatter


class MainTextExtractor(object):

    @classmethod
    def _remove_chars(cls, text):
        stripped = text.strip(' \t\n\r')
        if not stripped:
            return None
        else:
            return stripped

    @classmethod
    def _main_paragraph_text(cls, html):
        """
        Method to extract the main content by only looking
        at the html p tag elements.
        """

        soup = BeautifulSoup(html, 'html.parser')
        min_length = 30
        feature_text = []

        for p in soup.find_all('p'):
            text_content = MainTextExtractor._remove_chars(p.get_text(strip=True))
            if text_content and (len(text_content) > min_length):
                feature_text.append(text_content)

        return ' \n'.join(feature_text)

    @classmethod
    def removeCharacters(self, s):
        s = s.strip(' \t\n\r')
        if ((s == "") | (s==None)):
            return None
        return s

    @classmethod
    def _parse_tags(cls, html):

        excluded_tags = ['script', 'style', 'noscript', 'html', 'head', 'meta', 'header', 'footer',
                         'link', 'body', 'input', 'form', 'a']
        minimum_text_node_length = 8

        y_data = []
        text_data = []
        tag_signatures = []

        soup = BeautifulSoup(html, 'html.parser')

        for tag in soup.findAll():

            path = '.'.join(reversed([p.name for p in tag.parentGenerator() if p]))
            tag_signature = '.'.join([path, tag.name])

            if (tag.name not in excluded_tags) and ('table' not in path):

                tag_text = []
                for text in tag.contents:
                    if isinstance(text, Comment):
                        continue
                    try:
                        text = text.strip()
                        aux = BeautifulSoup(text, 'html.parser')
                        if aux.find() is None:
                            tag_text.append(text)
                    except Exception, e:
                        pass

                tag_text = "\n".join(tag_text)

                if tag_text and len(tag_text) > minimum_text_node_length:
                    if tag_text not in text_data:

                        # Remove line returns and tabs
                        tag_text = cls._remove_chars(tag_text)
                        if tag_text:
                            y_data.append(len(tag_text))
                            text_data.append(tag_text)
                            tag_signatures.append(path)

        x = np.array(y_data)
        return x, text_data, tag_signatures

    @classmethod
    def _find_intervals(cls, x):
        """
        The main content is ofteb located between two points l_ini and l_end.
        This method aims to find two pointers where the distance between l_ini
        and l_end is minimum and the number of characters between
        these pointers is maximum.
        """
        x = np.array(x)
        x_length = x.shape[0]
        total = np.sum(x)
        mean = np.mean(x)

        # Locate where the maximum is
        max_pointer = np.argmax(x)
        max_accum = 0
        pointer_left, pointer_right = max_pointer, max_pointer

        # Find tags higher than average in the left neighbourhood until there
        # is no hope
        hope_left_state, hope_right_state = True, True
        while pointer_left > 0 and hope_left_state:
            # if the x[pointer_left - 1] is greater than the mean, move
            # the pointer one to the left
            if x[pointer_left - 1] > mean:
                pointer_left -= 1
            else:
                # Is it worth to move to the left? If yes, there is hope.
                pointer_left_hope = pointer_left - 5
                if pointer_left_hope < 0:
                    pointer_left_hope = 0

                hope_left = x[pointer_left_hope:pointer_left][::-1]
                max_hope_left_value = np.max(hope_left)
                max_hope_left_idx = pointer_left - np.argmax(hope_left) - 1

                if max_hope_left_value > mean:
                    pointer_left = max_hope_left_idx
                else:
                    hope_left_state = False

        # Same reasoning as previous one but for the right
        while (pointer_right + 1) < x_length and hope_right_state:
            if x[pointer_right + 1] > mean:
                pointer_right += 1
            else:
                # Is it worth to move to the right?
                pointer_right_hope = pointer_right + 5

                if pointer_right_hope > len(x):
                    pointer_right_hope = len(x)

                hope_right = x[(pointer_right + 1): pointer_right_hope]
                max_hope_right_value = np.max(hope_right)
                max_hope_right_idx = pointer_right + np.argmax(hope_right) + 1

                if max_hope_right_value > mean:
                    pointer_right = max_hope_right_idx
                else:
                    hope_right_state = False

        # Find a cutoff pointer where the number of characters on the left is
        # equal to the number of characters on the right.
        # This is just for visualization
        accumulated = 0
        for i in xrange(0, x_length):
            accumulated += x[i]
            if accumulated >= (total / 2):
                cutoff_point = i
                break

        return pointer_left - 1, pointer_right + 1, cutoff_point, mean, max_pointer

    @classmethod
    def _refine_intervals(cls, max_tag_signature, max_pointer, text_data, l_ini, l_end):
        """
        This method runs after findIntervals and intends to narrow down
        where the left and right pointers are.
        """

        max_tag_signature_parts = max_tag_signature[max_pointer].split('.')
        tag_max_match = np.zeros(l_end)

        for i in xrange(l_ini, l_end):
            tag_signature_aux_parts = max_tag_signature[i].split('.')
            max_match = 0

            for j in range(0, len(max_tag_signature_parts)):
                try:
                    if max_tag_signature_parts[j] == tag_signature_aux_parts[j]:
                        max_match = j
                    else:
                        break
                except IndexError, e:
                    break

            tag_max_match[i] = max_match

        tag_max_match = np.asarray(tag_max_match, dtype='float64')
        min_max_scaler = preprocessing.MinMaxScaler()
        tag_max_match = min_max_scaler.fit_transform(tag_max_match.reshape(-1, 1))

        tag_max_match = tag_max_match.reshape(1, -1)[0]

        return l_ini, l_end, tag_max_match

    @classmethod
    def _combined_tags_text(cls, html):

        x, text_data, tag_signatures = MainTextExtractor._parse_tags(html)
        # print x
        if x.any():
            l_ini, l_end, cutoff_point, mean, max_pointer = MainTextExtractor._find_intervals(x)
            l_ini, l_end, tag_max_match = MainTextExtractor._refine_intervals(tag_signatures, max_pointer, text_data, l_ini, l_end)

            final_text = []
            for i in xrange(l_ini, l_end):
                if tag_max_match[i] > 0.65:
                    final_text.append(text_data[i])

            # This is only for debugging - Plot the html distribution
            # import matplotlib.pyplot as plt
            # mean_line = [mean] * x.shape[0]
            # #std = np.std(y_data)

            # plt.figure(1)
            # plt.subplot(211)
            # plt.plot(x)
            # plt.plot(mean_line)
            # plt.axvline(x=cutoff_point,linewidth=2, color='purple')
            # plt.axvline(x=l_ini,linewidth=2, color='r')
            # plt.axvline(x=l_end,linewidth=2, color='r')
            # plt.ylabel('Num Characters')
            # plt.xlabel('Tag Location')
            # plt.title('Content Distribution in HTML Page')
            # plt.show()

            return '\n'.join(final_text)
        else:
            return None

    @classmethod
    def _goose_cleaned_text(cls, html, page_html):
        article = Article()
        article.raw_html = html
        article.raw_doc = page_html
        article.doc = article.raw_doc

        goose_extractor = ContentExtractor(Configuration(), article)
        goose_cleaner = DocumentCleaner(Configuration(), article)
        goose_formatter = OutputFormatter(Configuration(), article)
        # goose_image_extractor = ImageExtractor(Configuration(), article) use

        try:
            article.doc = goose_cleaner.clean()
            article.top_node = goose_extractor.calculate_best_node()
            if article.top_node is not None:
                article.top_node = goose_extractor.post_cleanup()
                article.cleaned_text = goose_formatter.get_formatted_text()
        except UnicodeDecodeError, e:
            article.top_node = None

        return article.cleaned_text

    @classmethod
    def extract(cls, html, page_html):
        return [MainTextExtractor._goose_cleaned_text(html, page_html),
                MainTextExtractor._combined_tags_text(html),
                MainTextExtractor._main_paragraph_text(html)]

if __name__ == '__main__':
    # this packages should be here but we only need the for improving the
    # extractor therefore it might interfere with the rest of the project
    mE = MainTextExtractor()
    target_url = 'http://www.toshiba-aircon.co.uk/products/refrigerant-leak-detection-solutions/refrigerant-leak-detection-solutions/rbc-aip4'
    article = Goose().extract(target_url)
    print mE.extract(article.raw_html, article.raw_doc)