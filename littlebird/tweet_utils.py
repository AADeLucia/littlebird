"""
Various utilities to handle opening and writing Tweets to a file.

Author: Alexandra DeLucia
"""
# Standard imports
import logging
import os
import gzip
import zlib
import tarfile
import zipfile

# Third-party imports
import jsonlines as jl
import filetype

# Configure logging
logging.basicConfig(level=logging.INFO)


class TweetReader:
    """Iterator to read a Twitter file"""
    def __init__(self, filename):
        try:
            ftype = filetype.guess(filename).extension
            if ftype == "gz":
                self.f = gzip.open(filename, "r")
            else:
                self.f = open(filename, "r")
        except Exception as err:
            logging.error(f"Issue opening {filename}:\n{err}")
    
    def read_tweets(self):
        try:
            with jl.Reader(self.f) as reader:
                for tweet in reader.iter(skip_empty=True, skip_invalid=True):
                    yield tweet
        except (ValueError) as err:
           logging.error(f"Error encountered in tweet:\n{tweet}") 


if __name__ == "__main__":
    reader = TweetReader("/home/aadelucia/files/minerva/data/tweets_en/2014_01_01_MA.gz")
    for tweet in reader.read_tweets():
        print(tweet)
        break

