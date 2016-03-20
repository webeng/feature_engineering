from __future__ import division
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk.collocations import *
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import sys
import string
import cPickle
import pyfscache
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join, split
import copy_reg
import types
nltk.data.path = ['/Users/joanfihu/nltk_data', '/Users/Joan/nltk_data', '/Users/sb/nltk_data', '/usr/share/nltk_data',
				'/usr/local/share/nltk_data', '/usr/lib/nltk_data', '/usr/local/lib/nltk_data', '/home/ubuntu/nltk_data']

path = "./"
#path = "/home/www/brain/"
cache_it = pyfscache.FSCache(path + 'cache', days=10, hours=12, minutes=30)

# We had to add this to methods to be able to add new types to joblib pickle
def _pickle_method(method):
	func_name = method.im_func.__name__
	obj = method.im_self
	cls = method.im_class
	return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
	for cls in cls.mro():
		try:
			func = cls.__dict__[func_name]
		except KeyError:
			pass
	return func.__get__(obj, cls)

copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)


class KeywordsExtractor(object):

	num_kewyords = 0
	data_path = './data/'
	stemmer = PorterStemmer()
	verbose = None

	def __init__(self, num_kewyords=10, data_path='./data/', verbose=False):
		self.num_kewyords = num_kewyords
		self.data_path = data_path
		self.verbose = verbose

	def stem_tokens(self, tokens):
		return [self.stemmer.stem(item) for item in tokens]

	def tokenize(self, text):
		soup = BeautifulSoup(text, 'html.parser')
		text = soup.getText()
		text = filter(lambda x: x in string.printable, text)
		lowers = str(text).lower()
		text = lowers.translate(None, string.punctuation)
		tokens = nltk.word_tokenize(text)
		stems = tokens
		#stems = self.stem_tokens(tokens)
		return stems

	def get_bbc_news_corpus(self):
		news_corpus = []
		for news_type in ['business', 'entertainment', 'politics', 'sport', 'tech']:
			mypath = self.data_path + 'bbc/' + news_type
			onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
			for file_name in onlyfiles:
				f = open(self.data_path + 'bbc/' + news_type + '/' + file_name, 'r')
				news_corpus.append(f.read().decode('utf-8', 'replace'))
				f.close()

		return news_corpus

	def train_tfidf(self, tokenizer='custom', corpus='news'):

		if tokenizer == 'custom':
			tokenizer = self.tokenize

		nltk_corpus = []
		if corpus == 'all':
			nltk_corpus += [nltk.corpus.gutenberg.raw(f_id) for f_id in nltk.corpus.gutenberg.fileids()]
			nltk_corpus += [nltk.corpus.webtext.raw(f_id) for f_id in nltk.corpus.webtext.fileids()]
			nltk_corpus += [nltk.corpus.brown.raw(f_id) for f_id in nltk.corpus.brown.fileids()]
			nltk_corpus += [nltk.corpus.reuters.raw(f_id) for f_id in nltk.corpus.reuters.fileids()]
		elif corpus == 'news':
			nltk_corpus += self.get_bbc_news_corpus()

		if self.verbose:
			print "LENGTH nltk corpus corpus: {}".format(sum([len(d) for d in nltk_corpus]))


		vectorizer = TfidfVectorizer(
			max_df=1.0,
			min_df=2,
			encoding='utf-8',
			decode_error='strict',
			max_features=None,
			stop_words='english',
			ngram_range=(1, 3),
			norm='l2',
			tokenizer=tokenizer,
			use_idf=True,
			sublinear_tf=False)

		vectorizer.fit_transform(nltk_corpus)

		output = open(self.data_path + 'train_tfidf_vectorizer.pkl', 'wb')
		cPickle.dump(vectorizer, output, protocol=-1)
		output.close()
		return vectorizer

	def extract_bigrams(self, text):

		text = self.remove_return_lines_and_quotes(text)
		bigrams = []

		st = PorterStemmer()
		stop = stopwords.words('english')

		more_stop_words = [
			'(', ')', "'s", ',', ':', '<', '>', '.', '-', '&', '*', '...']
		stop = stopwords.words('english')
		stop = stop + more_stop_words

		tokens = st.stem(text)
		tokens = nltk.word_tokenize(tokens.lower())
		tokens = [i for i in tokens if i not in stop]
		tokens = [word for word in tokens if len(word) > 2]

		bigram_measures = nltk.collocations.BigramAssocMeasures()
		finder = BigramCollocationFinder.from_words(tokens)
		finder.apply_freq_filter(2)
		top_bigrams = finder.nbest(bigram_measures.pmi, 1000)

		for bg in top_bigrams:
			bg = " ".join(bg)
			tag = nltk.pos_tag([bg])[0]

			if tag[1] not in ['VBG', 'RB', 'VB', 'VBD', 'VBN', 'VBP', 'VBZ', 'PRP', 'IN', 'DT', 'CC', 'PRP$']:
				bigrams.append(tag[0])

		return bigrams

	@cache_it
	def get_tfidf_model(self):
		pkl_file = open(self.data_path + 'train_tfidf_vectorizer.pkl', 'rb')
		vectorizer = cPickle.load(pkl_file)
		pkl_file.close()
		return vectorizer

	def remove_return_lines_and_quotes(self, text):
		text = text.replace('\n', ' ')
		text = text.replace('\t', ' ')
		text = text.replace('\r', ' ')
		text = text.replace('"', '')
		return text

	def extract(self, documents=None, vectorizer=None, tokenizer='custom', tfidf_corpus='news'):

		try:
			vectorizer = self.get_tfidf_model()
		except IOError, e:
			vectorizer = self.train_tfidf(tokenizer, tfidf_corpus)
		except UnboundLocalError:
			#cache_it.clear()
			cache_it.purge()
			vectorizer = self.get_tfidf_model()

		docs = vectorizer.transform(documents)
		feature_names = vectorizer.get_feature_names()
		features = []
		for i in xrange(docs.shape[0]):

			sort_score_indices = np.argsort(docs[i, :].data)
			top_n_indices = self.num_kewyords if (len(sort_score_indices)) > self.num_kewyords else len(sort_score_indices)

			#top_keywords = vectorizer.get_feature_names()[docs[i,:].indices[np.argsort(docs[i,:].data)[::-1][:1]]]
			top_features_indices = []
			if top_n_indices:
				top_features_indices = docs[i, :].indices[np.argsort(docs[i, :].data)[::-1][:top_n_indices]]

			# print "Top Feature Indices: {}".format(top_features_indices)

			# for j in docs[i,:].indices:
			# print "Relevance: {}, Index: {} Features Name:
			# {}".format(docs[i,j], j, feature_names[j])

			# print "Top features: "
			top_features_names = [feature_names[f] for f in top_features_indices]

			# Extract most common bigrams. TFIDF gives more relevance to
			# unigrams than bigrams
			bigrams = self.extract_bigrams(documents[i])
			top_features_names = list(set(top_features_names + bigrams))

			features.append(top_features_names)

		return features

if __name__ == '__main__':
	k = KeywordsExtractor(num_kewyords=10, verbose=True, data_path='/Applications/MAMP/htdocs/article_data_mining/data/')
	document = "Iain Duncan Smith has criticised the government's desperate search for savings in his first interview since resigning as work and pensions secretary."
	print k.extract(documents=[document])[0]
	#print k.train_tfidf()
	#print k.get_tfidf_model()
