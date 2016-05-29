# publinx
A simple tool to make files available in an otherwise non-public directory. Intended to be used with nginx + uWSGI + Python 3 + Flask.

I made this because I [synchronize](https://www.syncthing.net/) my data to my server and sometimes want other people to access certain files. With this tool, I can selectively give out access by simply editing a JSON file in my synchronized directory.

publinx can serve files and simple directory listings under their original or rewritten paths, can make links expire after a certain date and implements password protection via GET parameters or HTTP authentication. Although there should be no obvious security vulnerabilities in the code, I do not recommend using this in a situation where security is critical.

This project is licensed under GPLv3, so please create beautiful things with it.

publinx was mostly created at the very awesome [Gulaschprogrammiernacht](https://gulas.ch/).


# Table of contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Creating public links](#creating-public-links)

# Installation
publinx is a uWSGI "app".

For the installation of uWSGI and Python 3, consult a guide you trust.

Additionally, install the Python module python-dateutil.

Point uWSGI to `module=publinx` and `callable=app`.


# Configuration
Copy config.sample.py to config.py, change BASEDIR to your data directory and, if needed, change the name of the config file.


# Creating public links

All configuration takes place in the link file `.publinx.json`, which contains basic JSON syntax.

Be careful as there are no checks for valid but stupid configurations. If you want to make your home directory or your link file publicly available, I won't stop you.


## Simple file output
To simply return a file with the same path as it has in your directory, add it as a key to the link file:
```json
{
    "simple-file.ext": {}
}
```
This file can now be accessed via `http://www.example.com/simple-file.ext`.

publinx also supports files in subfolders, you can add `folder/file.ext` to return this file.


## URL Rewriting
If you want to return a file from a different URL, use the public filename as the key and add a `path` parameter to the values:
```json
{
    "public-filename.ext": {
        "path": "folder/hidden-filename.ext"
    }
}
```
Now, the file at `folder/hidden-filename.ext` will transparently be returned when `http://www.example.com/public-filename.ext` is requested. This also works for directory listings.


## Publishing a folder listing
To publish the contents of a folder, add it to the configuration like you would with a regular file.

If you make all folders and files in this directory available, add `"recursive": true` to the setting.

```json
{
    "directory/with/subdirectories": {
        "recursive": true
    }
}
```
To exclude certain files or subfolders from the directory, place them in an `exclude` list. Note that the most specific configuration always wins, in the example below, the file `still-available.file` can be acessed although it is in an excluded directory. Of course, this also works for subdirectories.
```json
{
    "directory": {
        "recursive": true,
        "exclude": [
            "secret",
            "top-secret.file"
        ]
    },
    "directory/secret/still-available.file": {}
}
```

## Password protection
The most simple way to protect a file with a password is to require a GET parameter. This can be achieved by adding a parameter `password` to the file's entry.
```json
{
    "secret.file": {
        "password": "hunter2"
    }
}
```
Now you can only access this file via http://www.example.com/secret.file?password=hunter2. If the wrong password or no password is given, it acts as if the file does not exist and returns a 404 error to avoid obviously leaking information.


## HTTP Authentication
A more advanced way of protecting your files is via HTTP authentication. publinx supports plain-text and hashed passwords. For hashing, Python's [hashlib.pbkdf2_hmac](https://docs.python.org/3/library/hashlib.html#hashlib.pbkdf2_hmac) with sha256 is used. The other parameters can be set in the configuration.
```json
{
    "passwordprotected.file": {
        "auth": {
            "plaintextuser": "plaintextpassword",
            "hasheduser": {
                "hash": "3767f805a4558892f16fa0e3809043cc59170e5aac22534db508888bb11cb0cf",
                "salt": "mysalt",
                "rounds": 100000
            }
        }
    }
}
```
The password protected file can now be accessed via HTTP authentication with `plaintextuser`/`plaintextpassword` or `hasheduser`/`password`.

To generate a password hash, use Python code similar to these lines:
```python
import hashlib, binascii
dk = hashlib.pbkdf2_hmac('sha256', b'password', b'mysalt', 100000)
binascii.hexlify(dk)
```

## Expiring links

To create a link that expires after a certain time, add a parameter `expires` with a ISO 8601 formatted date and time (or any other string that can be parsed by `dateutil.parser.parse`). After this time (on the server), the link won'be accessible any more and return 404.
```json
{
    "datedfile": {
        "expires": "2016-05-29T01:34:00+0200"
    }
}
```
