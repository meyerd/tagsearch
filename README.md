TagSearch
=========

Index your music database tags and search later in the
index database. This is for everyone, who does not use
a music player with a search database or just wants to
find specific files where filenames do not reflect the
real content.

Packages required
-----------------

```
python-woosh
python-mutagen
python-argparse
```

Usage
-----

First you have to index your music files with

`./create_database.py --db tagdb /path/to/files`.

This will create a new directory `tagdb` in the 
current directory and initialize an empty database
there. If the database already exists, it is loaded
and information is added to it.

You can search using

`./search.py --db tagdb <search term>`.

`./search.py -h` provides a quick overview over the
search expression syntax and a more extensive
documentation can be found 
[here](http://pythonhosted.org/Whoosh/querylang.html).
