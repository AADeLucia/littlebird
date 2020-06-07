"""
Various utilities to handle opening and writing Tweets to a file.

Author: Alexandra DeLucia
"""
# Standard imports
import logging
import sys
import gzip
import zlib

# Third-party imports
import jsonlines as jl
import filetype

# Configure logging
logging.basicConfig(level=logging.INFO)


class TweetReader:
    """Iterator to read a Twitter file"""

    def __init__(self, filename):
        self.path = filename

        try:
            self.ftype = filetype.guess(filename).extension
        except AttributeError as err:
            # filetype could not be determined
            self.ftype = None

        try:
            if self.ftype == "gz":
                self.f = gzip.open(filename, "r")
            else:
                self.f = open(filename, "r")
        except Exception as err:
            logging.error(f"Issue opening {filename}:\n{err}")
            sys.exit(1)

    def read_tweets(self):
        try:
            with jl.Reader(self.f) as reader:
                for tweet in reader.iter(skip_empty=True, skip_invalid=True):
                    yield tweet
        except (UnicodeDecodeError, gzip.BadGzipFile, zlib.error) as err:
            logging.error(f"Error reading {self.path} of type {self.ftype}: {err}")
            self.f.close()
            sys.exit(1)

        # Close file
        self.f.close()
        return


class TweetWriter:
    """Write Tweets in jsonlines format"""

    def __init__(self, filename):
        self.path = filename
        try:
            if ".gz" in filename:
                self.f = gzip.open(filename, "w+")
            else:
                self.f = open(filename, "w+")
        except Exception as err:
            logging.error(f"Issue opening {filename}:\n{err}")
            sys.exit(1)

    def write(self, tweets):
        """Write Tweet or list of Tweets to file"""
        with jl.Writer(self.f) as writer:
            if not isinstance(tweets, list):
                writer.write(tweets)
            else:
                writer.write_all(tweets)
        self.f.close()


if __name__ == "__main__":
    reader = TweetReader(
        "/home/aadelucia/files/minerva/data/tweets_en/2014_01_01_MA.gz"
    )
    for tweet in reader.read_tweets():
        print(tweet)
        break
