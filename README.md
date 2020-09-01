# Little Bird

Basic utilties for processing Tweets. Includes:  
* `TweetTokenizer` for tokenizing the Tweet content
* `TweetReader` for easily iterating over Tweets
* `TweetWriter` for conveniently writing one or more Tweets to a file in JSONlines format

## Installation
There are two options for installing `littlebird`.

### 1. Install from source
```bash
git clone https://github.com/AADeLucia/littlebird.git
cd littlebird
python setup.py develop
```

### 2. Install with `pip`
```bash
pip install git+git://github.com/AADeLucia/littlebird.git#egg=littlebird
```


## Read and Write a Tweet JSONlines file
The example below reads in a Tweet file, filters to Tweets that have a hashtag, and writes out to a new file.

`TweetWriter`can write a single Tweet or list of Tweets to a file in JSONlines format. It will also automatically open a GZIP file if the provided filename has a `.gz` extension. If you are writing to a GZIP file, it is recommended to write all Tweets at once instead of writing incrementally; this provides better file compression. If you do need to write incrementally, I recommend writing to a normal file and GZIPping after.

```python
from littlebird import TweetReader, TweetWriter

# File in JSONlines form. Automatically handles GZIP files.
tweet_file = "2014_01_02.json.gz"
reader = TweetReader(tweet_file)

# Iterate over Tweets
# Save Tweets that contain hashtags
filtered_tweets = []
for tweet in reader.read_tweets():
    if tweet.get("truncated", False):
        num_hashtags = len(tweet["extended_tweet"]["entities"]["hashtags"])
    else:
        num_hashtags = len(tweet["entities"]["hashtags"])
    
    if num_hashtags > 0:
        filtered_tweets.append(tweet)

# Write out filtered Tweets
writer = TweetWriter("filtered.json")
writer.write(filtered_tweets)
```

You can also skip retweeted and quoted statuses

```python
for tweet in reader.read_tweets(skip_retweeted_and_quoted=True):
```

## Tokenize Tweets

There are multiple pre-defined tokenizers that are useful for different downstream usecases.

* **TweetTokenizer**: default customizable tokenizer
* **BERTweetTokenizer**: tokenizer based off the original BERTweet pre-processing from [the BERTweet model repo](https://github.com/VinAIResearch/BERTweet).
* **GloVeTweetTokenizer**: tokenizer based off a modified version of the [GloVe](https://nlp.stanford.edu/projects/glove/) preprocessor. It's based off of a modified version because the [original ruby processing script](https://nlp.stanford.edu/projects/glove/preprocess-twitter.rb) does not work.

You can also write your own tokenizer. Examples are below.

### Example usage
A basic example using the default Tokenizer settings is below.

```python
from littlebird import TweetReader, TweetTokenizer

# File in JSONlines form. Automatically handles GZIP files.
tweet_file = "2014_01_02.json.gz"
reader = TweetReader(tweet_file)
tokenizer = TweetTokenizer()

# Iterate over tweets and get the tokenized text.
# Automatically checks for retweeted and quoted text except if
# tokenizer = TweetTokenizer(include_retweeted_and_quoted_content=False)
for tweet in reader.read_tweets():
    # Tokenize the Tweet's text
    tokens = tokenizer.get_tokenized_tweet_text(tweet)

    # Get tweet hashtags. Also includes hashtags from retweeted and quoted statuses
    hashtags = tokenizer.get_hashtags(tweet)
```

You can directly access the internal `tokenize` method with `tokenizer.tokenize(text)`.

If you do not need to skip over tweets and only need the text, then you can use the `tokenize_tweet_file()` method. This method gets the tokenized text from the entire tweet (retweet, quoted, and full text). 

```python
from littlebird import TweetTokenizer

tweet_file = "2014_01_02.json.gz"
tokenizer = TweetTokenizer()

# Returns a tokenized string for each tweet
tokenized_tweets = tokenizer.tokenize_tweet_file(tweet_file)

# Returns a list of tokens for each tweet
tokenized_tweets = tokenizer.tokenize_tweet_file(tweet_file, return_tokens=True)
```

### Tokenizer settings
Available `TweetTokenizer` settings:

* `language`: right now it only really supports English, but as long as you change the `token_pattern` accordingly, it should work with other languages. A future integration is using `Moses` for Arabic tokenization.
* `token_pattern`: Pattern to match for acceptable tokens. Default is `r"\b\w+\b"`
* `stopwords`: provide a list of stopwords to remove from the text. Default is `None` for no stopword removal.
* `remove_hashtags`: Default is `False` to keep hashtags in the text (only strips the "#" symbol)
* `lowercase`: Default is `True` to lowercase all of the text. Change this to `False` if you are doing case-sensitive tasks like Name Entity Recognition (NER)

The tokenizer works in the following steps:

1. Remove hashtags (optional)
2. Remove URLs, handles, and "RT"
3. Lowercase the text (optional)
4. Find all tokens that match the `token_pattern` with `regex.findall(token_pattern, text)`
5. Remove stopwords (optional)


#### Token patterns
The token pattern is extremely important to set for your use case. Below are some sample token patterns, but I highly recommend [refreshing on your regular expressions](http://www.regular-expressions.info/tutorial.html) if you need something more advanced.

**Note:** the `regex` package is used to access character classes like `\p{L}`. Basically [Java regex patterns](http://www.regular-expressions.info/tutorial.html).

* `r"\b\w+\b"` matches any token with one or more letters, numbers, and underscores. This is equivalent to `"[\p{L}\_\p{N}]+"`
* `r"\b\p{L}+\b"` matches any token with one or more "letters" (across all alphabets).
* `r"\b[\w']\b` matches any token with one or more letters, numbers, and underscores. This pattern also preserves apostraphes "'", which is useful for not splitting contractions (e.g. not "can't" -> "can t"). It does not preserve quotes (e.g. "She said 'hello'" -> "she said hello")


### Writing your own tokenizer

If you would like to write your own, simply extend the `BaseTweetTokenizer` class. See below and `tweet_tokenizer.py` for examples.

```python
from littlebird import BaseTweetTokenizer

class NewTweetTokenizer(BaseTweetTokenizer):
    def __init__(self, include_retweeted_and_quoted_content = True):
        # Initialize super class
        super().__init__(include_retweeted_and_quoted_content)

        # Define class variables and settings
        self.token_pattern = "aa*"

    # Overwrite the tokenize method
    def tokenize(self, tweet):
        regex.findall(self.token_pattern, tweet)
        return 
    
    # Define any helper methods as needed
    def _helper(self):
        return
```

---

This package is a work in progress. Feel free to open any issues you run into or recommend features. I started this package for my own NLP research with tweets. 

```
@misc{DeLucia2020,
    author = {Alexandra DeLucia},
    title = {Little Bird},
    year = {2020},
    publisher = {GitHub},
    journal = {GitHub repository},
    howpublished = {\url{https://github.com/aadelucia/littlebird}},
}
```

Copyright (c) 2020 Alexandra DeLucia

