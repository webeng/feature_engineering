import nltk
import requests


class Entities(object):

	def remove_return_lines_and_quotes(self, text):
		text = text.replace('\n', ' ')
		text = text.replace('\t', ' ')
		text = text.replace('\r', ' ')
		text = text.replace('"', '')
		return text

	def extract(self, text, entity_description=False):
		# We need to clean the text in each method otherwise when we present it
		# to the user, it will have a different format
		text = self.remove_return_lines_and_quotes(text)
		sentences = [nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(text)]

		# This function is quite expensive
		sentences = [nltk.pos_tag(sent) for sent in sentences]

		entities_all = {} if entity_description else []

		#stop = stopwords.words('english')
		# more_stop_words = ['(' , ')', "'s" , ',', ':' , '<' , '>' , '.' , '-' , '&' ,'*','...' , 'therefore' , '.vs','hence']
		# stop = stopwords.words('english')
		# stop = stop + more_stop_words
		stop = ["a", "able", "about", "above", "abst", "accordance", "according", "accordingly", "across", "act", "actually", "added", "adj", "affected", "affecting", "affects", "after", "afterwards", "again", "against", "ah", "all", "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "an", "and", "announce", "another", "any", "anybody", "anyhow", "anymore", "anyone", "anything", "anyway", "anyways", "anywhere", "apparently", "approximately", "are", "aren", "arent", "arise", "around", "as", "aside", "ask", "asking", "at", "auth", "available", "away", "awfully", "b", "back", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "begin", "beginning", "beginnings", "begins", "behind", "being", "believe", "below", "beside", "besides", "between", "beyond", "biol", "both", "brief", "briefly", "but", "by", "c", "ca", "came", "can", "cannot", "can't", "cause", "causes", "certain", "certainly", "co", "com", "come", "comes", "contain", "containing", "contains", "could", "couldnt", "d", "date", "did", "didn't", "different", "do", "does", "doesn't", "doing", "done", "don't", "down", "downwards", "due", "during", "e", "each", "ed", "edu", "effect", "eg", "eight", "eighty", "either", "else", "elsewhere", "end", "ending", "enough", "especially", "et", "et-al", "etc", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "except", "f", "far", "few", "ff", "fifth", "first", "five", "fix", "followed", "following", "follows", "for", "former", "formerly", "forth", "found", "four", "from", "further", "furthermore", "g", "gave", "get", "gets", "getting", "give", "given", "gives", "giving", "go", "goes", "gone", "got", "gotten", "h", "had", "happens", "hardly", "has", "hasn't", "have", "haven't", "having", "he", "hed", "hence", "her", "here", "hereafter", "hereby", "herein", "heres", "hereupon", "hers", "herself", "hes", "hi", "hid", "him", "himself", "his", "hither", "home", "how", "howbeit", "however", "hundred", "i", "id", "ie", "if", "i'll", "im", "immediate", "immediately", "importance", "important", "in", "inc", "indeed", "index", "information", "instead", "into", "invention", "inward", "is", "isn't", "it", "itd", "it'll", "its", "itself", "i've", "j", "just", "k", "keep	keeps",
				"kept", "kg", "km", "know", "known", "knows", "l", "largely", "last", "lately", "later", "latter", "latterly", "least", "less", "lest", "let", "lets", "like", "liked", "likely", "line", "little", "'ll", "look", "looking", "looks", "ltd", "m", "made", "mainly", "make", "makes", "many", "may", "maybe", "me", "mean", "means", "meantime", "meanwhile", "merely", "mg", "might", "million", "miss", "ml", "more", "moreover", "most", "mostly", "mr", "mrs", "much", "mug", "must", "my", "myself", "n", "na", "name", "namely", "nay", "nd", "near", "nearly", "necessarily", "necessary", "need", "needs", "neither", "never", "nevertheless", "new", "next", "nine", "ninety", "no", "nobody", "non", "none", "nonetheless", "noone", "nor", "normally", "nos", "not", "noted", "nothing", "now", "nowhere", "o", "obtain", "obtained", "obviously", "of", "off", "often", "oh", "ok", "okay", "old", "omitted", "on", "once", "one", "ones", "only", "onto", "or", "ord", "other", "others", "otherwise", "ought", "our", "ours", "ourselves", "out", "outside", "over", "overall", "owing", "own", "p", "page", "pages", "part", "particular", "particularly", "past", "per", "perhaps", "placed", "please", "plus", "poorly", "possible", "possibly", "potentially", "pp", "predominantly", "present", "previously", "primarily", "probably", "promptly", "proud", "provides", "put", "q", "que", "quickly", "quite", "qv", "r", "ran", "rather", "rd", "re", "readily", "really", "recent", "recently", "ref", "refs", "regarding", "regardless", "regards", "related", "relatively", "research", "respectively", "resulted", "resulting", "results", "right", "run", "s", "said", "same", "saw", "say", "saying", "says", "sec", "section", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sent", "seven", "several", "shall", "she", "shed", "she'll", "shes", "should", "shouldn't", "show", "showed", "shown", "showns", "shows", "significant", "significantly", "similar", "similarly", "since", "six", "slightly", "so", "some", "somebody", "somehow", "someone", "somethan", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "specifically", "specified", "specify", "specifying", "still", "stop", "strongly", "sub", "substantially", "successfully", "such", "sufficiently", "suggest", "sup", "sure"]

		for s in sentences:
			chunked = nltk.ne_chunk(s, binary=True)
			for n in chunked:
				if isinstance(n, nltk.tree.Tree):
					if n.label() == 'NE':
						entities_all = self.getEntity(n, stop, entities_all, entity_description)

		if entity_description:
			return entities_all
		else:
			return list(set(entities_all))

	def getEntity(self, n, stop, entities_all, entity_description=None):
		entity = None

		for c in n:
			entity = c[0] if not entity else entity + " " + c[0]

		entity_lower = entity.lower()
		entity_lower = [i for i in [entity_lower] if i not in stop]

		if entity_lower:
			if entity_description:
				entity_dbpedia = self.lookup_entity(entity)
				entities_all[entity_dbpedia['name']] = entity_dbpedia
			else:
				entities_all.append(entity)

		return entities_all

	def lookup_entity(self, entity):
		entity_dbpedia = {}
		entity_dbpedia['name'] = entity
		entity_dbpedia['categories'] = []
		entity_dbpedia['classes'] = []
		entity_dbpedia['description'] = None

		headers = {
			'content-type': 'application/json',
			'Accept': 'application/json'
		}

		r = requests.get('http://lookup.dbpedia.org/api/search/PrefixSearch?MaxHits=2&QueryString=' + entity, headers=headers)

		if r.status_code == 200:
			r_json = r.json()
			if r_json['results']:
				try:
					entity_dbpedia['description'] = r_json['results'][0]['description']
				except KeyError, e:
					pass

				try:
					entity_dbpedia['categories'] = r_json['results'][0]['categories'][0]
				except KeyError, e:
					pass

				try:
					entity_dbpedia['classes'] = r_json['results'][0]['classes']
				except KeyError, e:
					pass

		return entity_dbpedia

if __name__ == '__main__':
	e = Entities()
	text = "Iain Duncan Smith has criticised the government's desperate search for savings in his first interview since resigning as work and pensions secretary."
	print e.extract(text, entity_description=True)
