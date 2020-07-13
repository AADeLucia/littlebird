"""
Add the URL titles to all tweets in passed tweet JSON

URL titles are in new field "url_titles". This is in a separate script
since URL requests are more time consuming than basic parsing.

Author: Alexandra DeLucia
"""
# Standard imports
import logging
import argparse
import os

# Local imports
from littlebird import TweetReader
from littlebird import TweetWriter
from littlebird import TweetTokenizer

# Configurations
logging.basicConfig(level=logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-files", nargs="+", required=True)
    parser.add_argument("--output-dir", type=str, required=True)
    parser.add_argument("--include-retweeted-content", action="store_true", 
        help="Search entities in retweeted and quoted statuses in addition to the original tweet")
    return parser.parse_args()


if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_args()

    # Initialize tokenizer
    tokenizer = TweetTokenizer(include_retweeted_and_quoted_content=args.include_retweeted_content)

    # Loop through files
    for input_file in args.input_files:
        modified_tweets = []
        reader = TweetReader(input_file)
        for tweet in reader.read_tweets():
            temp = tokenizer.add_url_titles(tweet)
            modified_tweets.append(temp)
        
        # Write out tweets
        output_file = os.path.join(args.output_dir, input_file)
        writer = TweetWriter(output_file)
        writer.write(modified_tweets)

