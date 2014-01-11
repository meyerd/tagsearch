#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Search the tag database index for some regular
expression.

The database will be created in the current directory
and named `tagdb` by default.
"""

import argparse
import textwrap
import os
import logging
import datetime
import sys

from whoosh.fields import Schema, TEXT, DATETIME, ID
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser, PhrasePlugin, \
    SequencePlugin, FuzzyTermPlugin

logging.basicConfig(level=logging.DEBUG)


schema = Schema(path=ID(stored=True),
                tags=TEXT(stored=True),
                last_updated=DATETIME(stored=True))


def search_for(search_term, index, limit=10):
    mparser = MultifieldParser(["path", "tags"], schema=schema)
    mparser.remove_plugin_class(PhrasePlugin)
    mparser.add_plugin(SequencePlugin())
    mparser.add_plugin(FuzzyTermPlugin())

    try:
        query = mparser.parse(search_term)
        logging.debug("parsed search query %s" % (repr(query)))
    except Exception as e:
        logging.error("error parsing search query '%s'" %
                      (repr(search_term)))
        return

    logging.info("searching ... ")

    with index.searcher() as searcher:
        results = searcher.search(query, limit=limit)
        logging.info("found %i results" % len(results))
        logging.info("outputting paths names ...")
        for n, hit in enumerate(results):
            #print "%i: %s" % (n, hit['path'].encode(sys.stdout.encoding))
            print "%i: %s" % (n, hit['path'].encode(sys.stdout.encoding))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''\
Open a tag database and search for the supplied
search term.

Search language
---------------
The search language is specified at:
   http://pythonhosted.org/Whoosh/querylang.html

Basics are:

- Boolean operators: AND OR NOT ANDNOT
    pink AND floyd
- Phrases: " ... "
    "pink floyd"
- Maximum distance of words: floyd can have a maximum
  distance of 5 to pink:
    "pink floyd"~5
- Wildcards: ? for one character, * for several characters,
  but be aware that wildcards do not match across terms:
    "p?nk fl*d"
  but
    "pin*oyd"
  does not match "pink floyd".
- Lexical ranges:
    [apple TO bear]
  will match azores and be but not blur.
- Fuzzy queries by specifying the edit distance:
    cat~
  will match cast (insert s), at (delete c), and act
  (transpose c and a).
    cat~2
  will match bat (delete c and insert b, two edits).
    johannson~2/3
        will match with edit distance 2, but the first 3
  characters have to match exactly (prefix).
    johannson~/3
  will force the prefix length to be 3.

''')
    parser.add_argument('search_term', metavar='search term',
                        type=str, help='''Search term for the text
                        to search in the tag database.''', nargs='+')
    parser.add_argument('--db', dest='database', type=str,
                        default='tagdb',
                        help='''Database directory''')
    parser.add_argument('-l', dest='limit', type=int,
                        default=-1, help='''Limit number of search
                        results (default: -1 means all results)''')

    args = parser.parse_args()

    tagdb_directory = args.database
    search_term = u' '.join([i.decode(sys.stdin.encoding)
                             for i in args.search_term])
    limit = args.limit

    logging.debug("tagdb_directory: %s" % (tagdb_directory))
    logging.debug("search_term: %s" % (repr(search_term)))
    logging.debug("limit: %i" % (limit))

    logging.info("tag database in %s" % (tagdb_directory))
    if not os.path.exists(tagdb_directory):
        logging.error("tagdb not found in %s" % (tagdb_directory))
        sys.exit(1)
    try:
        index = open_dir(tagdb_directory)
    except Exception:
        logging.error("error opening tag db")
        sys.exit(1)

    if limit < 1:
        limit = None
    search_for(search_term, index, limit=limit)
