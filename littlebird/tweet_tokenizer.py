"""
General utilities to open a Twitter file.

Author: Alexandra DeLucia
"""
# Standard imports
import os
import argparse
import logging
import gzip
import zlib
from collections import Counter
import random

# Third-party imports
import jsonlines as jl
import regex

# Local modules
from littlebird import TweetReader

# Configurations
logging.basicConfig(level=logging.INFO)

# Define erros
class Error(Exception):
    pass


class LanguageNotSupportedError(Error):
    def __init__(self, lang):
        self.lang = lang


# Define tokenizer class
class TweetTokenizer:
    """
    Open Twitter files and process the text content.
    """
    def __init__(self, 
        language="en",
        token_pattern=r"\b\w+\b",
        stopwords=None,
        remove_hashtags=False,
        lowercase=True
        ):
        """
        Currently only English and Arabic are support languages ("en" and "ar").
        There are many options for the token pattern, and the token pattern should be different depending upon your use case.
        Default: r"\b\w+\b"
        Only letters: "\p{L}+"
        Letters and numbers: "[\p{L}\p{N}]+"
        Starts with a letter but can contain numbers: "\p{L}[\p{L}\p{N}]+"
        The default stopwords None does not remove stopwords
        User handle pattern: r"(?<![A-Za-z0-9_!@#\$%&*])@(([A-Za-z0-9_])    {20}(?!@))|(?<![A-Za-z0-9_!@#\$%&*])@(([A-Za-z0-9_]){1,19})(?![A-Za-    z0-9_]*@)"
        Retweet pattern: r"\bRT\b"
        URL pattern: r"http(s)?:\/\/[\w\.\/\?\=]+" 
        """
        # Current compatibility
        if language not in ["en", "ar"]:
            raise LanguageNotSupportedError(language)
        else:
            self.language = language

        # Handle pattern from NLTK
        self.HANDLE_RE = r"(?<![A-Za-z0-9_!@#\$%&*])@(([A-Za-z0-9_]){20}(?!@))|(?<![A-Za-z0-9_!@#\$%&*])@(([A-Za-z0-9_]){1,19})(?![A-Za-z0-9_]*@)"
        self.URL_RE = r"http(s)?:\/\/[\w\.\/\?\=]+"
        self.RT_RE = r"\bRT\b"
        self.HASHTAG_RE = regex.compile(r"#[\p{L}\p{N}_]+")
        self.REMOVAL_RE = regex.compile("|".join([self.HANDLE_RE, self.URL_RE, self.RT_RE]))
        self.WHITESPACE_RE = regex.compile(r"\s+")
        self.TOKEN_RE = regex.compile(token_pattern)
        self.remove_hashtags = remove_hashtags
        self.lowercase = lowercase
        if stopwords is not None:
            self.stopwords = set(stopwords)
        else:
            self.stopwords = None
        return

    def tokenize(self, tweet):
        """
        :param tweets:
        :return: tokens
        """
        if self.remove_hashtags:
            tweet = self.HASHTAG_RE.sub(" ", tweet)

        # Remove URLs, handles, "RT"
        tweet = self.REMOVAL_RE.sub(" ", tweet)
        
        # Lowercase
        if self.lowercase:
            tweet = tweet.lower()
        
        # Tokenize
        tokens = self.TOKEN_RE.findall(tweet)

        # Remove stopwords
        if self.stopwords:
            tokens = [t for t in tokens if t not in self.stopwords]
        return tokens


    def tokenize_tweet_file(self, input_file, sample_size=-1, return_tokens=False):
        """
        Return tokenize tweets in file

        :param input_file: path to input file
        :param sample_size: size of sample to take of tweets. The sample is min(sample, number of tweets in file)
        """
        # Get all tweet content
        all_tweet_text = []
        reader = TweetReader(input_file)
        for tweet in reader.read_tweets():
            if "extended_tweet" in tweet:
                text = tweet["extended_tweet"]["full_text"]
            else:
                text = tweet["text"]
            all_tweet_text.append(text)

        num_tweets = len(all_tweet_text)
        # Check for empty file
        if num_tweets == 0:
            logging.warning(f"{input_file} has no tweets.")
            return

        # Sample from the file's tweets
        if sample_size != -1:
            if sample_size < num_tweets:
                all_tweet_text = random.sample(all_tweet_text, k=sample_size)
        
        # Tokenize the tweets and return
        # Some tweets have no valid tokens. Skip them.
        tweet_text = map(self.tokenize, all_tweet_text)
        if return_tokens:
            tweet_text = [t for t in tweet_text if t != []]
        else:
            tweet_text = [" ".join(t) for t in tweet_text if t != []]
        return tweet_text


def parse_args():
    """Command-line parser for use with scripting"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-files", type=str, nargs="+", help="List of GZIP'd Tweet files")
    parser.add_argument("--sample", type=int, default=-1, help="Number of tweets to use for the keyword counts. Only for Tweet files.")
    parser.add_argument("--language", choices=["en", "ar"])
    parser.add_argument("--output-dir")
    parser.add_argument("--output-file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    tokenizer = TweetTokenizer(remove_hashtags=True)
    tweet_text = tokenizer.tokenize_tweet_file("/home/aadelucia/files/minerva/raw_tweets/tweets_en/2014_01_01_MA.gz", sample_size=10)
    print(tweet_text)


