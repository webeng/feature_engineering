from textblob import TextBlob


def findSentiment(keywords):

	k_aux = {}
	for k in keywords:
		blob = TextBlob(k)
		k_aux[k] = {}

		if blob.sentiment.polarity < 0:
			k_aux[k]['word'] = 'negative'
		elif blob.sentiment.polarity > 0:
			k_aux[k]['word'] = 'positive'
		else:
			k_aux[k]['word'] = 'neutral'

		k_aux[k]['sentiment'] = blob.sentiment.polarity
		k_aux[k]['subjectivity'] = blob.sentiment.subjectivity
	keywords = k_aux

	return keywords

def getSentimentText(text):
	item_aux = {}
	blob = TextBlob(text)

	if blob.sentiment.polarity < 0:
		item_aux['word'] = 'negative'
	elif blob.sentiment.polarity > 0:
		item_aux['word'] = 'positive'
	else:
		item_aux['word'] = 'neutral'

	item_aux['sentiment'] = blob.sentiment.polarity
	item_aux['subjectivity'] = blob.sentiment.subjectivity

	return item_aux

if __name__ == '__main__':
	text = '''
	The titular threat of The Blob has always struck me as the ultimate movie
	monster: an insatiably hungry, amoeba-like mass able to penetrate
	virtually any safeguard, capable of--as a doomed doctor chillingly
	describes it--"assimilating flesh on contact.
	Snide comparisons to gelatin be damned, it's a concept with the most
	devastating of potential consequences, not unlike the grey goo scenario
	proposed by technological theorists fearful of
	artificial intelligence run rampant.
	'''
	print getSentimentText(text)