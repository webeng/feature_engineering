# Feature Engineering
Methods to extract features from text and links. The features can be used to improve your application or by machine learning algorithms. Some of the methods are geared towards news articles but they also work with other domains. If you are not a Python programmer or need to do feature engineering at a larger scale, you can use [the API](https://market.mashape.com/adlegant/article-analysis) 

## Installation
```
git clone git@github.com:webeng/feature_engineering.git
cd feature_engineering
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

Run `python link.py` to see an example.


## author.py
Extracts who is the author of an article given a URL.

## category.py
Classify a document

## entities.py
Extracts the entities in the document

## feeds.py
Extract all the feed urls in a single page

## images.py (to be added)
Extracts images in a HTML document and ranks them by surface.

## keywords.py
Extracts main keywords in a text document using term frequency-inverse document frequency.

## sentiment.py
Analyses the sentiment of a text or keyword. Uses the module textblob

## title.py
Extracts potential page titles including.
