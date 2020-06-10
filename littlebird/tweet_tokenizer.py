"""
General utilities to open a Twitter file.

Author: Alexandra DeLucia
"""
# Standard imports
import argparse
import logging
import random

from typing import Iterable, List, Optional, Set, Union, Dict

# Third-party imports
import regex

# Local modules
from littlebird import TweetReader

# Configurations
logging.basicConfig(level=logging.INFO)


class LanguageNotSupportedError(ValueError):
    def __init__(self, lang: str):
        self.lang = lang

#####
# Settings
#####
# Supported languages
support_langs: [Iterable[str]] = set(["en"])

# List curated by Keith Harriggian
# Only supports English
CONTRACTIONS: Dict[str, str] =  { 
    "ain't": "is not",
    "aren't": "are not",
    "can't": "can not",
    "can't've": "can not have",
    "cannot": "can not",
    "'cause": "because",
    "could've": "could have",
    "couldn't": "could not",
    "couldn't've": "could not have",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hadn't've": "had not have",
    "hasn't": "has not",
    "haven't": "have not",
    "he'd": "he would",
    "he'd've": "he would have",
    "he'll": "he will",
    "he'll've": "he will have",
    "he's": "he is",
    "how'd": "how did",
    "how'd'y": "how do you",
    "how'll": "how will",
    "how's": "how is",
    "i'd": "i would",
    "i'd've": "i would have",
    "i'll": "i will",
    "i'll've": "i will have",
    "i'm": "i am",
    "i've": "i have",
    "isn't": "is not",
    "it'd": "it would",
    "it'd've": "it would have",
    "it'll": "it will",
    "it'll've": "it will have",
    "it's": "it is",
    "let's": "let us",
    "ma'am": "madam",
    "mayn't": "may not",
    "might've": "might have",
    "mightn't": "might not",
    "mightn't've": "might not have",
    "must've": "must have",
    "mustn't": "must not",
    "mustn't've": "must not have",
    "needn't": "need not",
    "needn't've": "need not have",
    "o'clock": "of the clock",
    "oughtn't": "ought not",
    "oughtn't've": "ought not have",
    "shan't": "shall not",
    "sha'n't": "shall not",
    "shan't've": "shall not have",
    "she'd": "she would",
    "she'd've": "she would have",
    "she'll": "she will",
    "she'll've": "she will have",
    "she's": "she is",
    "should've": "should have",
    "shouldn't": "should not",
    "shouldn't've": "should not have",
    "so've": "so have",
    "so's": "so is",
    "that'd": "that would",
    "that'd've": "that would have",
    "that's": "that is",
    "there'd": "there would",
    "there'd've": "there would have",
    "there's": "there is",
    "they'd": "they would",
    "they'd've": "they would have",
    "they'll": "they will",
    "they'll've": "they will have",
    "they're": "they are",
    "they've": "they have",
    "to've": "to have",
    "wasn't": "was not",
    "we'd": "we would",
    "we'd've": "we would have",
    "we'll": "we will",
    "we'll've": "we will have",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    "what'll": "what will",
    "what'll've": "what will have",
    "what're": "what are",
    "what's": "what is",
    "what've": "what have",
    "when's": "when is",
    "when've": "when have",
    "where'd": "where did",
    "where's": "where is",
    "where've": "where have",
    "who'll": "who will",
    "who'll've": "who will have",
    "who's": "who is",
    "who've": "who have",
    "why's": "why is",
    "why've": "why have",
    "will've": "will have",
    "won't": "will not",
    "won't've": "will not have",
    "would've": "would have",
    "wouldn't": "would not",
    "wouldn't've": "would not have",
    "y'all": "you all",
    "y'all'd": "you all would",
    "y'all'd've": "you all would have",
    "y'all're": "you all are",
    "y'all've": "you all have",
    "you'd": "you would",
    "you'd've": "you would have",
    "you'll": "you will",
    "you'll've": "you will have",
    "you're": "you are",
    "you've": "you have",
    "that'll": "that will",
}


#####
# Define tokenizer class
#####
class TweetTokenizer:
    """
    Open Twitter files and process the text content.
    """

    def __init__(
        self,
        language: str = "en",
        token_pattern: str = r"\b\w+\b",
        stopwords: Optional[Iterable[str]] = None,
        remove_hashtags: bool = False,
        lowercase: bool = True,
        expand_contractions: bool = True
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
        if language not in supported_langs:
            raise LanguageNotSupportedError(language)
        else:
            self.language = language

        # Handle pattern from NLTK
        self.HANDLE_RE = r"(?<![A-Za-z0-9_!@#\$%&*])@(([A-Za-z0-9_]){20}(?!@))|(?<![A-Za-z0-9_!@#\$%&*])@(([A-Za-z0-9_]){1,19})(?![A-Za-z0-9_]*@)"
        self.URL_RE = r"http(s)?:\/\/[\w\.\/\?\=]+"
        self.RT_RE = r"\bRT\b"
        self.HASHTAG_RE = regex.compile(r"#[\p{L}\p{N}_]+")
        self.REMOVAL_RE = regex.compile(
            "|".join([self.HANDLE_RE, self.URL_RE, self.RT_RE])
        )
        self.WHITESPACE_RE = regex.compile(r"\s+")
        self.TOKEN_RE = regex.compile(token_pattern)
        self.remove_hashtags = remove_hashtags
        self.lowercase = lowercase
        self.stopwords: Optional[Set[str]]
        if stopwords is not None:
            self.stopwords = set(stopwords)
        else:
            self.stopwords = None
        self.expand_contractions = expand_contractions
        return

    def tokenize(self, tweet: str) -> List[str]:
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

        # Remove contractions (only matches lowercase)
        if self.expand_contractions:
            for contraction, expanded in CONTRACTIONS.items():
                tweet = regex.sub(contraction, expanded, tweet)

        # Tokenize
        tokens = self.TOKEN_RE.findall(tweet)

        # Remove stopwords
        if self.stopwords:
            tokens = [t for t in tokens if t not in self.stopwords]
        return tokens

    def tokenize_tweet_file(
        self, input_file: str, sample_size: int = -1, return_tokens: bool = False
    ) -> Optional[Union[List[str], List[List[str]]]]:
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
            return None

        # Sample from the file's tweets
        if sample_size != -1:
            if sample_size < num_tweets:
                all_tweet_text = random.sample(all_tweet_text, k=sample_size)

        # Tokenize the tweets and return
        # Some tweets have no valid tokens. Skip them.
        tweet_text_ = map(self.tokenize, all_tweet_text)
        tweet_text: Union[List[str], List[List[str]]]
        if return_tokens:
            tweet_text = [t for t in tweet_text_ if t != []]
        else:
            tweet_text = [" ".join(t) for t in tweet_text_ if t != []]
        return tweet_text


def parse_args() -> argparse.Namespace:
    """Command-line parser for use with scripting"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-files", type=str, nargs="+", help="List of GZIP'd Tweet files"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=-1,
        help="Number of tweets to use for the keyword counts. Only for Tweet files.",
    )
    parser.add_argument("--language", choices=["en", "ar"])
    parser.add_argument("--output-dir")
    parser.add_argument("--output-file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    tokenizer = TweetTokenizer(remove_hashtags=True)
    tweet_text = tokenizer.tokenize_tweet_file(
        "/home/aadelucia/files/minerva/raw_tweets/tweets_en/2014_01_01_MA.gz",
        sample_size=10,
    )
    print(tweet_text)
