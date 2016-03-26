# Feature Engineering
The repository contains modules to extract features from text and web pages. The features can be uses as a training data for machine algorithms or to improve your applications. Some of the methods are geared towards news articles but they also work with other domains. If you are not a Python programmer or need to do feature engineering at a larger scale, you can use [the API](https://market.mashape.com/adlegant/article-analysis) 

## Installation
```
git clone git@github.com:webeng/feature_engineering.git
cd feature_engineering
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

Run `python link.py` to see an example.

If you want fast keyword extraction, you will have to [install HDFS](http://www.hdfgroup.org/ftp/HDF5/current/src/unpacked/release_docs/INSTALL). Also, you might have to install pytables by running this command `sudo HDF5_DIR=/usr/local/hdf5/ pip install tables`.  Also add /usr/local/hdf5/lib/ to LD_LIBRARY_PATH. I'll try develop a slower version without the HDFS.

# Modules
You can run each module individually to see examples.

## author.py
Extracts the author of an article given a link.

## category.py
Classify a document

## entities.py
Named entity recognition.

## feeds.py
Extracts feed urls given a link.

## images.py (to be added)
Extracts images in a HTML document and ranks them by surface.

## main_text.py (to be added)
Extracts the main text of page given a url.

## keywords.py
Extracts main keywords in a text document using term frequency-inverse document frequency.

## sentiment.py
Analyses the sentiment of a text or keyword.

## title.py
Extracts page titles.
