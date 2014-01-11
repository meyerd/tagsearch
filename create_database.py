#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create a searchable index database for searching tags
of music files in a specific subdirectory.

The database will be created in the current directory
and named `tagdb` by default.
"""

import argparse
import os
import logging
import datetime

from whoosh.fields import Schema, TEXT, DATETIME, ID
from whoosh.index import create_in, open_dir

import mutagen


#logging.basicConfig(level=logging.DEBUG)


schema = Schema(path=ID(stored=True),
                tags=TEXT(stored=True),
                last_updated=DATETIME(stored=True))


def create_db_if_neccessary(directory):
    if not os.path.exists(directory):
        logging.debug("tagdb not found, creating new one in %s" %
                     (directory))
        os.mkdir(directory)
        ix = create_in(directory, schema)
        return ix
    logging.debug("opening tagdb in %s" % (directory))
    ix = open_dir(directory)
    return ix


def traverse(directory, index, remove_nonexistent=False):
    for dirname, subdirlist, filelist in os.walk(directory):
        logging.info("entering directory %s" % (dirname))
        writer = index.writer()
        for filename in filelist:
            fullpath = os.path.join(directory, dirname, filename)
            logging.info(" processing file %s" % (filename))
            try:
                mf = mutagen.File(fullpath, easy=True)
            except Exception as e:
                logging.warn("  mutagen error %s" % (repr(e)))
                continue
            if not mf:
                logging.debug("  unsupported file type.")
            else:
                try:
                    logging.debug("  found taginfo: %s" % (repr(mf)))
                    try:
                        indextext = u' '.join([item for sublist in
                                               mf.values() for item
                                               in sublist])
                    except TypeError:
                        indextext = u' '.join([repr(item) for sublist in
                                              mf.values() for item in
                                              sublist])
                    writer.add_document(path=fullpath, tags=indextext,
                                        last_updated=datetime.datetime.now())
                except Exception as e:
                    logging.warn("  unknown error %s" % (repr(e)))
        writer.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='''Traverse the directory <base directory> and
                       record filenames and tags to an indexable
                       database for later searching''')
    parser.add_argument('base_directory', metavar='<base directory>',
                        type=str, help='Base directory to traverse.')
    parser.add_argument('--db', dest='database', type=str,
                        default='tagdb',
                        help='''Database directory. If the database
                        already exists, then it will be updated''')
#    parser.add_argument('--remove-nonexistent', action='store_true',
#                        default=False, help='''Remove nonexistend files
#                        already in the database.''')

    args = parser.parse_args()

    tagdb_directory = args.database
    base_directory = unicode(args.base_directory)
#    remove_nonexistent = args.remove_nonexistent
    remove_nonexistent = False

    logging.debug("tagdb_directory: %s" % (tagdb_directory))
    logging.debug("base_directory: %s" % (base_directory))
    logging.debug("remove_nonexistent: %s" % (remove_nonexistent))

    logging.info("tag database in %s" % (tagdb_directory))
    index = create_db_if_neccessary(tagdb_directory)
    logging.info("traversing %s" % (base_directory))
    traverse(base_directory, index, remove_nonexistent)
