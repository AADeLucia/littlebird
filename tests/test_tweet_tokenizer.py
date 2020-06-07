#!/usr/bin/env python3
"""
Tests for littlebird/tweet_tokenizer.py
"""
import unittest
from typing import List

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


if __name__ == "__main__":
    unittest.main()
