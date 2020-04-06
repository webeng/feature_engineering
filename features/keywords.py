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
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join, split
import cProfile
import pstats
import tables
import numpy as np
import csv
from pprint import pprint
nltk.data.path = ['home/ubuntu/nltk_data', '/Users/joanfihu/nltk_data', '/usr/share/nltk_data', '/usr/local/share/nltk_data', '/usr/lib/nltk_data', '/usr/local/lib/nltk_data' ,'/home/ubuntu/nltk_data']


class KeywordsExtractor(object):

	num_kewyords = 0
	data_path = './data/'
	stemmer = PorterStemmer()
	verbose = None

	def __init__(self, num_kewyords=10, data_path='../data/', verbose=False):
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

	def tokenize2(self, text):
		lowers = str(text).lower()
		text = lowers.translate(None, string.punctuation)
		return nltk.word_tokenize(text)

	def get_bbc_news_corpus(self):
		news_corpus = []
		for news_type in ['business', 'entertainment', 'politics', 'sport', 'tech']:
			mypath = self.data_path + 'bbc/' + news_type
			onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
			for file_name in onlyfiles:
				f = open(self.data_path + 'bbc/' + news_type + '/' + file_name, 'r')

				text = f.read().decode('utf-8', 'replace')

				soup = BeautifulSoup(text, 'html.parser')
				text = soup.getText()
				text = filter(lambda x: x in string.printable, text)
				lowers = str(text).lower()
				text = lowers.translate(None, string.punctuation)

				news_corpus.append(text)
				f.close()

		return news_corpus

	def get_specifiedby_corpus(self):
		specifiedby_corpus = []
		with open(self.data_path + 'specifiedby_corpus.csv', 'rU') as csvfile:
			reader = csv.reader(csvfile, delimiter=',', quotechar='"')
			header = next(reader)

			processed, failed = 0, 0
			for row in reader:
				if row:
					try:
						specifiedby_corpus.append(self.remove_non_ascii(row[0] + ' ' + row[1]))
						processed += 1
					except Exception, e:
						failed += 1
				else:
					failed += 1

		print "get_specifiedby_corpus - processed: {} failed {}".format(processed, failed)
		return specifiedby_corpus
		#return [" ".join(specifiedby_corpus)]

	def remove_non_ascii(self, text):
		"""
			Removes non ascii characters by converting them to their integers 
			and then remove anythin above ref 128
			Parameters :
			- text: <string> text to remove characters
		"""
		return ''.join([i if ord(i) < 128 else ' ' for i in text])

	def train_tfidf(self, tokenizer='custom', corpus='news'):

		if tokenizer == 'custom':
			#tokenizer = self.tokenize
			tokenizer = self.tokenize2

		nltk_corpus = []
		if corpus == 'all':
			nltk_corpus += [nltk.corpus.gutenberg.raw(f_id) for f_id in nltk.corpus.gutenberg.fileids()]
			nltk_corpus += [nltk.corpus.webtext.raw(f_id) for f_id in nltk.corpus.webtext.fileids()]
			nltk_corpus += [nltk.corpus.brown.raw(f_id) for f_id in nltk.corpus.brown.fileids()]
			nltk_corpus += [nltk.corpus.reuters.raw(f_id) for f_id in nltk.corpus.reuters.fileids()]
		elif corpus == 'news':
			nltk_corpus += self.get_bbc_news_corpus()
			nltk_corpus += self.get_specifiedby_corpus()

		if self.verbose:
			print "LENGTH nltk corpus corpus: {}".format(sum([len(d) for d in nltk_corpus]))


		vectorizer = TfidfVectorizer(
			max_df=0.5,
			min_df=150,
			encoding='utf-8',
			decode_error='strict',
			max_features=None,
			stop_words='english',
			ngram_range=(1, 3),
			norm='l2',
			tokenizer=tokenizer,
			analyzer='word',
			use_idf=True,
			sublinear_tf=False)

		#vectorizer.fit_transform(nltk_corpus)
		vectorizer.fit(nltk_corpus)
		# Avoid having to pickle instance methods, we will set this method on on load
		vectorizer.tokenizer = None
		keys = np.array(vectorizer.vocabulary_.keys(), dtype=str)
		values = np.array(vectorizer.vocabulary_.values(), dtype=int)
		stop_words = np.array(list(vectorizer.stop_words_), dtype=str)

		with tables.openFile(self.data_path + 'tfidf_keys.hdf', 'w') as f:
			atom = tables.Atom.from_dtype(keys.dtype)
			ds = f.createCArray(f.root, 'keys', atom, keys.shape)
			ds[:] = keys

		with tables.openFile(self.data_path + 'tfidf_values.hdf', 'w') as f:
			atom = tables.Atom.from_dtype(values.dtype)
			ds = f.createCArray(f.root, 'values', atom, values.shape)
			ds[:] = values

		with tables.openFile(self.data_path + 'tfidf_stop_words.hdf', 'w') as f:
			atom = tables.Atom.from_dtype(stop_words.dtype)
			ds = f.createCArray(f.root, 'stop_words', atom, stop_words.shape)
			ds[:] = stop_words

		vectorizer.vocabulary_ = None
		vectorizer.stop_words_ = None

		with open(self.data_path + 'tfidf.pkl', 'wb') as fin:
			cPickle.dump(vectorizer, fin)

		vectorizer.vocabulary_ = dict(zip(keys, values))
		vectorizer.stop_words_ = stop_words

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

	def get_tfidf_model(self):
		with open(self.data_path + 'tfidf.pkl', 'rb') as pkl_file:
			vectorizer = cPickle.load(pkl_file)

		vectorizer.tokenizer = self.tokenize

		with tables.openFile(self.data_path + 'tfidf_keys.hdf', 'r') as f:
			keys = f.root.keys.read()

		with tables.openFile(self.data_path + 'tfidf_values.hdf', 'r') as f:
			values = f.root.values.read()

		vectorizer.vocabulary_ = dict(zip(keys, values))

		with tables.openFile(self.data_path + 'tfidf_stop_words.hdf', 'r') as f:
			vectorizer.stop_words_ = set(f.root.stop_words.read())

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
		except (EOFError, IOError), e:
			vectorizer = self.train_tfidf(tokenizer, tfidf_corpus)

		docs = vectorizer.transform(documents)

		feature_names = vectorizer.get_feature_names()
		features = []
		for i in xrange(docs.shape[0]):

			sort_score_indices = np.argsort(docs[i, :].data)
			top_n_indices = self.num_kewyords if (len(sort_score_indices)) > self.num_kewyords else len(sort_score_indices)
			top_features_indices = []

			if top_n_indices:
				top_features_indices = docs[i, :].indices[np.argsort(docs[i, :].data)[::-1][:top_n_indices]]

			top_features_names = [feature_names[f] for f in top_features_indices]

			# Extract most common bigrams. TFIDF gives more relevance to
			# unigrams than bigrams
			# bigrams = self.extract_bigrams(documents[i])
			# top_features_names = list(set(top_features_names + bigrams))

			features.append(top_features_names)

		return features

if __name__ == '__main__':
	k = KeywordsExtractor(num_kewyords=100, verbose=True, data_path='../data/')
	document = "Iain Duncan Smith has criticised the government's desperate search for savings in his first interview since resigning as work and pensions secretary."
	document = "High-quality, contemporary facing brick available with a smooth or textured finish. There are bricks. And there are bricks you can design with. If you're used to assuming a choice of one colour and one finish, why not choose a brick that can become part of your design process instead? The Oakland range of brick can add a spark to architectural designs - whether your next project is traditional, contemporary or avant-garde, choose from a broad range of precision facing bricks with dynamic colours that will help bring the final project to life. Oakland Brick is available in a range of 20 colour and texture combinations. LOW EFFLORESCENCE\r\n\r\nAG's brick range is free from soluble salt, meaning that Oakland Brick's levels of efflorescence are extremely low.\r\n\r\n\r\nCOMPLEMENTARY SPECIALS\r\n\r\nA range of complementary specials are available.\r\n\r\n\r\nBRE GREEN GUIDE 'A' RATED\r\n\r\nOakland Brick is produced in the UK from locally sourced materials and manufactured with 90 harvested rain water and 100 renewable energy in the production process.\n\nProperties: Smooth, Textured, 1, BS EN 7713, ISO 9001, ISO 14001, A+, F2, Frost Resistant, A1 Oakland Brick - A contemporary brick with clean, crisp lines"
	print k.extract(documents=[document])[0]
	# k.get_specifiedby_corpus()
	# cProfile.run("k.extract(documents=[document])[0]", 'restats')
	p = pstats.Stats('restats')
	p.sort_stats('cumulative').print_stats(30)


	#print k.train_tfidf()
	#print k.get_tfidf_model()
