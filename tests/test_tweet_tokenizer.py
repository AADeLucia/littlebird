#!/usr/bin/env python3
"""
Tests for littlebird/tweet_tokenizer.py
"""
import unittest
from typing import List, Dict, Any

import littlebird
from littlebird import TweetTokenizer


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

    def test_get_tokenized_tweet_text(self):
        return

    def test_tokenize_file(self):
        tokenizer = TweetTokenizer()
        text = tokenizer.tokenize_tweet_file("demo_tweets.json")

    def test_get_hashtags(self):
        return


if __name__ == "__main__":
    unittest.main()


