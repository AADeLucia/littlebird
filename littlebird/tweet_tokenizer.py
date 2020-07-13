"""
Tokenizes tweets either directly from a file or just from the passed-in text.

Author: Alexandra DeLucia
"""
# Standard imports
import argparse
import logging
import random
from typing import Iterable, List, Optional, Set, Union, Dict, Any

# Third-party imports
import regex

# Local modules
from littlebird import TweetReader
from littlebird import CONTRACTIONS

# Configurations
logging.basicConfig(level=logging.INFO)


class LanguageNotSupportedError(ValueError):
    def __init__(self, lang: str):
        self.lang = lang

# Settings
supported_langs: [Iterable[str]] = set(["en"])


# Define base tokenizer
class BaseTweetTokenizer:
    def __init__(self, include_retweet_and_quoted_content: bool = True):
        self.include_retweet_and_quoted_content = include_retweet_and_quoted_content
    
    def tokenize(self, tweet: str) -> List[str]:
        """This should be completed by child classes"""
        pass
    
    def get_tweet_text(self, tweet: Dict[str, Any]) -> str:
        """Return all text content from Tweet JSON"""
        # Check if tweet is truncated
        if tweet.get("truncated", False):
            text = tweet["extended_tweet"]["full_text"]
        else:
            text = tweet["text"]
        
        # Include retweeted/quoted content
        if self.include_retweet_and_quoted_content:
            if "quoted_status" in tweet:
                if tweet["quoted_status"].get("extended_tweet", False):
                    text += f" {tweet['quoted_status']['extended_tweet']['full_text']}"
                else:
                    text += f" {tweet['quoted_status']['text']}"
            if "retweeted_status" in tweet:
                if tweet["retweeted_status"].get("extended_tweet", False):
                    text += f" {tweet['retweeted_status']['extended_tweet']['full_text']}"
                else:
                    text += f" {tweet['retweeted_status']['text']}"
        return text

    def get_tokenized_tweet_text(self, tweet: Dict[str, Any]) -> str:
        """
        Convenience method. Returns all tokenized text from the Tweet. 
        Same as calling "get_tweet_text" and "tokenize" and then joining
        the token list into a string.
        """
        text = self.get_tweet_text(tweet)
        tokens = self.tokenize(text)
        return " ".join(tokens)

    def tokenize_tweet_file(
        self, input_file: str, sample_size: int = -1, return_tokens: bool = False
    ) -> Union[List[str], List[List[str]]]:
        """
        Return tokenize tweets in file

        :param input_file: path to input file
        :param sample_size: size of sample to take of tweets. The sample is min(sample, number of tweets in file)
        """
        # Get all tweet content
        reader = TweetReader(input_file)
        all_tweet_text = list(map(self.get_tweet_text, reader.read_tweets()))

        # Check for empty file
        num_tweets = len(all_tweet_text)
        if num_tweets == 0:
            return []
        
        # Sample from the Tweets
        # Only need to sample if sample_size > num_tweets
        if sample_size != -1:
            if sample_size < num_tweets:
                all_tweet_text = random.sample(all_tweet_text, k=sample_size)

        # Tokenize the Tweets
        # Skip the Tweets with only invalid tokens
        tweet_text = map(self.tokenize, all_tweet_text)

        # Join the tokens into a string if specified
        if return_tokens:
            tweet_text = [t for t in tweet_text if t != []]
        else:
            tweet_text = [" ".join(t) for t in tweet_text if t != []]
        return tweet_text
    
    def get_hashtags(self, tweet: Dict[str, Any]) -> List[str]:
        """Return all hashtags in Tweet. Includes hashtags in retweet
        if option is selected in init.
        """
        # Check if tweet is truncated
        if tweet.get("truncated", False):
            hashtags = tweet["extended_tweet"]["entities"]["hashtags"]
        else:
            hashtags = tweet["entities"]["hashtags"]
        
        # Include retweeted/quoted content
        if self.include_retweet_and_quoted_content:
            if "quoted_status" in tweet:
                if tweet["quoted_status"].get("extended_tweet", False):
                    hashtags.extend(tweet["quoted_status"]["extended_tweet"]["entities"]["hashtags"])
                else:
                    hashtags.extend(tweet["quoted_status"]["entities"]["hashtags"])
            if "retweeted_status" in tweet:
                if tweet["retweeted_status"].get("extended_tweet", False):
                    hashtags.extend(tweet["retweeted_status"]["extended_tweet"]["entities"]["hashtags"])
                else:
                    hashtags.extend(tweet["retweeted_status"]["entities"]["hashtags"])
        
        # Only return the text
        hashtags = [h.get("text") for h in hashtags]
        return hashtags

# Define tokenizer class
class TweetTokenizer(BaseTweetTokenizer):
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
        expand_contractions: bool = False,
        remove_lone_digits: bool = True,
        include_retweet_and_quoted_content: bool = True,
        replace_usernames_with: str = " ",
        replace_urls_with: str = " "
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
        # Initialize base class
        super().__init__(include_retweet_and_quoted_content)
        
        # Current compatibility
        if language not in supported_langs:
            raise LanguageNotSupportedError(language)
        else:
            self.language = language

        # Handle pattern from NLTK
        self.HANDLE_RE = regex.compile(r"(?<![A-Za-z0-9_!@#\$%&*])@(([A-Za-z0-9_]){20}(?!@))|(?<![A-Za-z0-9_!@#\$%&*])@(([A-Za-z0-9_]){1,19})(?![A-Za-z0-9_]*@)")
        self.URL_RE = regex.compile(r"http(s)?:\/\/[\w\.\/\?\=]+")
        self.RT_RE = regex.compile(r"\bRT\b")
        self.HASHTAG_RE = regex.compile(r"#[\p{L}\p{N}_]+")
        self.LONE_DIGIT_RE = regex.compile(r"\b\d+\b")
        self.WHITESPACE_RE = regex.compile(r"\s+")

        self.remove_hashtags = remove_hashtags
        self.lowercase = lowercase
        self.expand_contractions = expand_contractions
        self.remove_lone_digits = remove_lone_digits
        self.stopwords: Optional[Set[str]]
        if stopwords is not None:
            self.stopwords = set(stopwords)
        else:
            self.stopwords = None
        
        self.handle_sub = replace_usernames_with
        self.url_sub = replace_urls_with
        
        # Add handle and URL replacement strings
        # so they do not get parsed out
        if self.handle_sub.strip() != "":
            token_pattern += f"|{self.handle_sub}"
        if self.url_sub.strip() != "":
            token_pattern += f"|{self.url_sub}"
        self.TOKEN_RE = regex.compile(token_pattern)

    def tokenize(self, tweet: str) -> List[str]:
        """
        :param tweets:
        :return: tokens
        """
        if self.remove_hashtags:
            tweet = self.HASHTAG_RE.sub(" ", tweet)

        # Replace usernames
        tweet = self.HANDLE_RE.sub(self.handle_sub, tweet)

        # Replace URLs
        tweet = self.URL_RE.sub(self.url_sub, tweet)

        # Remove "RT"
        tweet = self.RT_RE.sub(" ", tweet)

        # Remove pesky ampersand
        tweet = regex.sub("(&amp)", " ", tweet)

        # Lowercase
        if self.lowercase:
            tweet = tweet.lower()
        
        # Expand contractions
        if self.expand_contractions:
            for contraction, expansion in CONTRACTIONS.items():
                tweet = regex.sub(contraction, expansion, tweet)

        # Remove lone digits (e.g. "4")
        if self.remove_lone_digits:
            tweet = self.LONE_DIGIT_RE.sub(" ", tweet)

        # Tokenize
        tokens = self.TOKEN_RE.findall(tweet)

        # Remove stopwords
        if self.stopwords:
            tokens = [t for t in tokens if t not in self.stopwords]
        return tokens


class GloVeTweetTokenizer(BaseTweetTokenizer):
    """
    Tokenizer that tokenizes like the GloVe pre-processor. 
    Original Ruby script here: https://nlp.stanford.edu/projects/glove/preprocess-twitter.rb
    """
    def __init__(self, include_retweet_and_quoted_content: bool = True):
        # Initialize base class
        super().__init__(include_retweet_and_quoted_content)
        
        self.URL_RE = regex.compile(r"https?:\/\/\S+\b|www\.(\w+\.)+\S*")
        self.HANDLE_RE = regex.compile(r"@\w+")
        self.NUMBER_RE = regex.compile(r"[-+]?[.\d]*[\d]+[:,.\d]*")
        self.HASHTAG_RE = regex.compile(r"#(\S+)")
        self.PUNCTUATION_RE = regex.compile(r"([!?.]){2,}")
        self.ELONG_RE = regex.compile(r"\b(\S*?)(.)\2{2,}\b")
        self.UPPER_TOKEN_RE = regex.compile(r"([A-Z]{2,})")

        # Emojis
        self.EMOJI_EYES = "[8:=;]"
        self.EMOJI_NOSE = "['`\-]?"
        self.EMOJI_SMILE_RE = regex.compile(self.EMOJI_EYES + self.EMOJI_NOSE + "[)dD]+|[)dD]+" + self.EMOJI_EYES + self.EMOJI_NOSE)
        self.EMOJI_LOL_RE = regex.compile(self.EMOJI_EYES + self.EMOJI_NOSE + "[pP]+")
        self.EMOJI_SAD_RE = regex.compile(self.EMOJI_EYES + self.EMOJI_NOSE + "\(+|\)+" + self.EMOJI_NOSE + self.EMOJI_EYES)
        self.EMOJI_NEUTRAL_RE = regex.compile(self.EMOJI_EYES + self.EMOJI_NOSE + "[\/|l*]")
        self.EMOJI_HEART_RE = regex.compile(r"<3")

    def tokenize(self, tweet: str) -> List[str]:
        # Replace URLs
        tweet = self.URL_RE.sub("<url>", tweet)
        
        # Replace emojis
        tweet = self.EMOJI_SMILE_RE.sub("<smile>", tweet)
        tweet = self.EMOJI_LOL_RE.sub("<lolface>", tweet)
        tweet = self.EMOJI_SAD_RE.sub("<sadface>", tweet)
        tweet = self.EMOJI_NEUTRAL_RE.sub("<neutralface>", tweet)
        tweet = self.EMOJI_HEART_RE.sub("<heart>", tweet)
        
        # From script: Force splitting words appended with slashes (once we tokenized the URLs, of course)
        tweet = regex.sub("/", " / ", tweet)

        # Replace handles
        tweet = self.HANDLE_RE.sub("<user>", tweet)

        # Replace numbers
        tweet = self.NUMBER_RE.sub("<number>", tweet)

        # Find all hashtags
        # Split hashtags into their subword components if possible
        tweet = self.HASHTAG_RE.sub(self._replace_hashtags, tweet)
        
        # Mark repeating punctuation
        # eg. "!!!" => "! <REPEAT>"
        tweet = self.PUNCTUATION_RE.sub(r" \1 <repeat> ", tweet)

        # Mark elongated words 
        # eg. "wayyyy" => "way <ELONG>"
        tweet = self.ELONG_RE.sub(r"\1\2 <elong> ", tweet)
 
        # Mark all uppercased tokens with <ALLCAPS>
        tweet = self.UPPER_TOKEN_RE.sub(self._replace_uppercase_tokens, tweet)
        
        # Lowercase all tokens
        tweet = tweet.lower()

        return tweet.split()
    
    def _replace_hashtags(self, match) -> str:
        """
        Returns a re-formatted version of the matched hashtag
        """
        hashtag = match.group(1)
        if hashtag.isupper():
            return f" <hashtag> {hashtag.lower()} <allcaps> "
        else:
            subwords = " ".join(regex.split(r"(?=[A-Z])", hashtag))
            return f" <hashtag> {subwords.lower()} "

    def _replace_uppercase_tokens(self, match) -> str:
        """
        Returns a lowercase string from the passed regex match object.
        """
        token = match.group(0)
        return token.lower() + " <allcaps> "


