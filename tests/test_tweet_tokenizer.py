#!/usr/bin/env python3
"""
Tests for littlebird/tweet_tokenizer.py
"""
import unittest
from typing import List

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


if __name__ == "__main__":
    unittest.main()


