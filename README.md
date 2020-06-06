# Little Bird

Basic utilties for processing Tweets. Includes:  
* TweetTokenizer for tokenizing the Tweet content
* TweetReader for easily iterating over tweets

## Installation
```bash
git clone https://github.com/AADeLucia/littlebird.git
cd littlebird
python setup.py develop
```

## Read a Tweet JSONlines file
The example below reads in a Tweet file and tokenizes all of the text.

```python
from littlebird import TweetReader
from littlebird import TweetTokenizer

# Initialize tokenizer with default settings
tokenizer = TweetTokenizer()

# File in JSONlines form. Automatically handles GZIP files.
tweet_file = "2014_01_02.json.gz"
reader = TweetReader(tweet_file)

# Iterate over Tweets
for tweet in reader.read_tweets():
    if tweet.get("truncated", False):
        text = tweet["extended_tweet"]["full_text"]
    else:
        text = tweet["text"]
    
    tokens = tokenizer.tokenize()
```


