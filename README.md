# articles_data_mining
Methods to extract features from text and links. Some of the methods are geared towards news articles but they also work well with other domains. Run `python link.py` to see an example of features that can be extracted given an link.

## Installation
`
git clone git@github.com:webeng/feature_engineering.git
cd feature_engineering
virtualenv env
source env/bin/activate
pip install -r requirements.txt
python link.py
`

# author.py
Extracts who is the author of an article given a URL.

# category.py
Classify a document

# entities.py
Extracts the entities in the document

# feeds.py
Extract all the feed urls in a single page

# images.py (to be added)
Extracts images in a HTML document and ranks them by surface.

# keywords.py
Extracts main keywords in a text document using term frequency-inverse document frequency.

# sentiment.py
Analyses the sentiment of a text or keyword. Uses the module textblob

#title.py
Extracts potential page titles including.
