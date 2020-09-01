#!/usr/bin/env python3
"""
Tests for littlebird/tweet_utils.py

Author: Alexandra DeLucia
"""
import unittest
from typing import List, Dict, Any

import littlebird
from littlebird import TweetReader
from littlebird import TweetWriter


class TestTweetReader(unittest.TestCase):
    def test_file_not_found(self):
        with self.assertRaises(SystemExit):
            reader = TweetReader("does_not_exist.json")

    def test_skip_retweets(self):
        reader = TweetReader("demo_tweets.json")
        for tweet in reader.read_tweets(skip_retweeted_and_quoted=True):
            self.assertEqual(tweet.get("retweeted_status", False), False)  
            self.assertEqual(tweet.get("quoted_status", False), False)     


if __name__ == "__main__":
    unittest.main()


