#!/usr/bin/env python3
"""
Tests for littlebird/tweet_tokenizer.py
"""
import unittest
from typing import List, Dict, Any

import littlebird
from littlebird import TweetTokenizer
from littlebird import GloVeTweetTokenizer


class TestTweetTokenizer(unittest.TestCase):
    def test_default_tokenize(self):
        tokenizer = TweetTokenizer()
        tweet: str = (
            "Me: I think I have Ebola       "
            "Doctor: when did you start feel"
            "ing symptoms       Me: bout a w"
            "eek ago       Everyone in hospi"
            "tal: http://t.co/LoIPKzvOmT"
        )
        tokenized = tokenizer.tokenize(tweet)
        right_answer: List[str] = [
            "me",
            "i",
            "think",
            "i",
            "have",
            "ebola",
            "doctor",
            "when",
            "did",
            "you",
            "start",
            "feeling",
            "symptoms",
            "me",
            "bout",
            "a",
            "week",
            "ago",
            "everyone",
            "in",
            "hospital",
        ]
        self.assertListEqual(tokenized, right_answer)

        # Quote handling
        tweet: str = "If people who are in love together are called \"Love Birds\" then people who always argue together should be called \"Angry Birds\"-happy nw yr"
        right_answer = ["if", "people", "who", "are", "in", "love", "together", "are", "called", "love", "birds", "then", "people", "who", "always", "argue", "together", "should", "be", "called", "angry", "birds", "happy", "nw", "yr"]
        tokenized = tokenizer.tokenize(tweet)
        self.assertListEqual(tokenized, right_answer)

    def test_supported_langs(self):
        with self.assertRaises(littlebird.tweet_tokenizer.LanguageNotSupportedError):
            tokenizer = TweetTokenizer(language="zxx")
        with self.assertRaises(littlebird.tweet_tokenizer.LanguageNotSupportedError):
            tokenizer = TweetTokenizer(language="es")
        with self.assertRaises(littlebird.tweet_tokenizer.LanguageNotSupportedError):
            tokenizer = TweetTokenizer(language="english")

    def test_contraction_expansion(self):
        tokenizer = TweetTokenizer(expand_contractions=True)
        tweet: str = "Why can't I #twerk"
        right_answer = ["why", "can", "not", "i", "twerk"]
        tokenized = tokenizer.tokenize(tweet)
        self.assertListEqual(tokenized, right_answer)

    def test_apostraphe_preservation(self):
        tokenizer = TweetTokenizer(token_pattern=r"\b[\w']+\b")
        tweet: str = "Why can't I ' #twerk '' :'( :')"
        right_answer = ["why", "can't", "i", "twerk"]
        tokenized = tokenizer.tokenize(tweet)
        self.assertListEqual(tokenized, right_answer)

        tweet: str = "She just wanted to say 'hello'"
        right_answer = ["she", "just", "wanted", "to", "say", "hello"]
        tokenized = tokenizer.tokenize(tweet)
        self.assertListEqual(tokenized, right_answer)
        
        tweet: str = "If people who are in love together are called \"Love Birds\" then people who always argue together should be called \"Angry Birds\"-happy nw yr"
        right_answer = ["if", "people", "who", "are", "in", "love", "together", "are", "called", "love", "birds", "then", "people", "who", "always", "argue", "together", "should", "be", "called", "angry", "birds", "happy", "nw", "yr"]
        tokenized = tokenizer.tokenize(tweet)
        self.assertListEqual(tokenized, right_answer)

    def test_remove_ampersand(self):
        tokenizer = TweetTokenizer()
        tweet: str = "@dr_m_badawy tnx u so much , the same for u &amp; all the best"
        right_answer = ["tnx", "u", "so", "much", "the", "same", "for", "u", "all", "the", "best"]
        tokenized = tokenizer.tokenize(tweet)
        self.assertListEqual(tokenized, right_answer)

    def test_remove_lone_digits(self):
        tokenizer = TweetTokenizer(remove_lone_digits=True)
        tweet: str = "luv 4 u"
        right_answer = ["luv", "u"]
        tokenized = tokenizer.tokenize(tweet)
        self.assertListEqual(tokenized, right_answer)

    def test_get_tweet_text(self):
        tokenizer = TweetTokenizer()
        tweet: Dict[str, Any] = {
            "text": "sample text",
            "truncated": True,
            "extended_tweet": {"full_text": "sample text plus more text"},
            "quoted_status": {"text": "quoted text", "extended_tweet": {"full_text": "quoted text and more text"}},
            "retweeted_status": {"text": "retweeted text", "extended_tweet": {"full_text": "retweeted text and more text"}}
        }
        right_answer = "sample text plus more text quoted text and more text retweeted text and more text"
        all_text = tokenizer.get_tweet_text(tweet)
        self.assertEqual(all_text, right_answer)

    def test_url_titles(self):
        tokenizer = TweetTokenizer()
        tweet = {"entities": {
            "urls": [
                {"url": "http://alexandradelucia.com", "expanded_url": "http://alexandradelucia.com"},
                {"url": "https://www.washingtonpost.com/news/voraciously/wp/2020/07/13/welcome-to-the-new-buffet-which-isnt-a-buffet-anymore/?utm_campaign=wp_post_most&utm_medium=email&utm_source=newsletter&wpisrc=nl_most", "expanded_url": "https://www.washingtonpost.com/news/voraciously/wp/2020/07/13/welcome-to-the-new-buffet-which-isnt-a-buffet-anymore/?utm_campaign=wp_post_most&utm_medium=email&utm_source=newsletter&wpisrc=nl_most"
                }
            ]
        }}
        right_answer = ["About · Alexandra DeLucia", "Welcome to the new buffet, which isn’t a buffet anymore - The Washington Post"]
        parsed_titles = tokenizer.add_url_titles(tweet).get("url_titles")
        self.assertEqual(right_answer, parsed_titles)

    def test_get_tokenized_tweet_text(self):
        return

    def test_tokenize_file(self):
        tokenizer = TweetTokenizer()
        text = tokenizer.tokenize_tweet_file("demo_tweets.json")

    def test_get_hashtags(self):
        return


class TestGloVeTweetTokenizer(unittest.TestCase):
    def test_uppercase_handling(self):
        tokenizer = GloVeTweetTokenizer()
        tweet = "OMG HAPPY"
        right_answer = ["omg", "<allcaps>", "happy", "<allcaps>"]
        self.assertEqual(tokenizer.tokenize(tweet), right_answer)

    def test_hashtag_handling(self):
        tokenizer = GloVeTweetTokenizer()
        tweet = "#splitMe #donotsplitme #UPPERCASE"
        right_answer = ["<hashtag>", "split", "me", "<hashtag>", "donotsplitme", "<hashtag>", "uppercase", "<allcaps>"]
        tokenized = tokenizer.tokenize(tweet)
        self.assertEqual(tokenized, right_answer)
    
    def test_emoji_handling(self):
        tokenizer = GloVeTweetTokenizer()
        tweet = ":D :d 8) 8-( :'/ :/ <3 ;) ;p"
        right_answer = ["<smile>", "<smile>", "<smile>", "<sadface>", "<neutralface>", 
            "<neutralface>", "<heart>", "<smile>", "<lolface>"]
        tokenized = tokenizer.tokenize(tweet)
        self.assertEqual(tokenized, right_answer)

    def test_punctuation_handling(self):
        tokenizer = GloVeTweetTokenizer()
        tweet = "hello there!!!"
        right_answer = ["hello", "there", "!", "<repeat>"]
        tokenized = tokenizer.tokenize(tweet)
        self.assertEqual(tokenized, right_answer)

    def test_word_elongation_handling(self):
        tokenizer = GloVeTweetTokenizer()
        tweet = "hellooooooo"
        right_answer = ["hello", "<elong>"]
        tokenized = tokenizer.tokenize(tweet)
        self.assertEqual(tokenized, right_answer)
 
    def test_number_handling(self):
        tokenizer = GloVeTweetTokenizer()
        tweet = "this is a Number 40"
        right_answer = ["this", "is", "a", "number", "<number>"]
        tokenized = tokenizer.tokenize(tweet)
        self.assertEqual(tokenized, right_answer)
 
    def test_url_handling(self):
        tokenizer = GloVeTweetTokenizer()
        tweet = "Check out this link http://t.co/dkfjkdf"
        right_answer = ["check", "out", "this", "link", "<url>"]
        tokenized = tokenizer.tokenize(tweet)
        self.assertEqual(tokenized, right_answer)
    
    def test_slash_split_handling(self):
        tokenizer = GloVeTweetTokenizer()
        tweet = "don't you wish this/that"
        right_answer = ["don't", "you", "wish", "this", "/", "that"]
        tokenized = tokenizer.tokenize(tweet)
        self.assertEqual(tokenized, right_answer)


if __name__ == "__main__":
    unittest.main()


