"""
Various utilities to handle opening and writing Tweets to a file.

Author: Alexandra DeLucia
"""
# Standard imports
import logging
import os
import sys
import gzip
import zlib

from typing import Any, Iterable, List, Union

# Third-party imports
import jsonlines as jl
import filetype

# Configure logging
logging.basicConfig(level=logging.INFO)


class TweetReader:
    """Iterator to read a Twitter file"""

    def __init__(self, filename: str):
        self.path = filename

        # Check if file exists
        if not os.path.exists(self.path):
            logging.error(f"File {self.path} does not exist.")
            sys.exit(1)
        
        # Get filetype
        try:
            self.ftype = filetype.guess(filename).extension
        except AttributeError as err:
            # filetype could not be determined
            self.ftype = None
        
        # Open file
        try:
            if self.ftype == "gz":
                self.f = gzip.open(filename, "r")
            else:
                self.f = open(filename, "r")
        except Exception as err:
            logging.error(f"Issue opening {filename}:\n{err}")
            sys.exit(1)

    def read_tweets(self,
        skip_deleted: bool = True,
        skip_withheld: bool = True,
        skip_retweeted_and_quoted: bool = False,
        print_stats: bool = False
    ) -> Iterable[Any]:
        # Initialize counters
        count_total = 0
        count_deleted = 0
        count_withheld = 0
        count_retweeted = 0
        try:
            with jl.Reader(self.f) as reader:
                for tweet in reader.iter(skip_empty=True, skip_invalid=True):
                    # Skip invalid tweets
                    if not isinstance(tweet, dict):
                        continue
                    count_total += 1
                    # Skip tweets that are marked as retweets
                    if skip_retweeted_and_quoted:
                        if "quoted_status" in tweet or "retweeted_status" in tweet:
                            count_retweeted += 1
                            continue
                    # Skip deleted tweets
                    if skip_deleted and "delete" in tweet:
                        count_deleted += 1
                        continue
                    # Skip 'status_withheld' tweets
                    if skip_withheld and "status_withheld" in tweet:
                        count_withheld += 1
                        continue
                    yield tweet
        except (UnicodeDecodeError, gzip.BadGzipFile, zlib.error) as err:
            logging.error(f"Error reading {self.path} of type {self.ftype}: {err}")
            self.f.close()
            sys.exit(1)

        # Close file
        self.f.close()
        # Print stats
        if print_stats:
            logging.warning(f"""
Total iterated tweets: {count_total:,}
Remaining tweets: {count_total - (count_deleted + count_withheld + count_retweeted):,}
Skipped tweets:
    Deleted: {count_deleted:,}
    Withheld: {count_withheld:,}
    Retweeted: {count_retweeted:,}""")
        return


class TweetWriter:
    """Write Tweets in jsonlines format"""

    def __init__(self, filename: str):
        self.path = filename
        try:
            if filename.endswith(".gz"):
                self.f = gzip.open(filename, "w+")
            else:
                self.f = open(filename, "w+")
        except Exception as err:
            logging.error(f"Issue opening {filename}:\n{err}")
            sys.exit(1)

    def write(self, tweets: Union[Any, List[Any]]) -> None:
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
