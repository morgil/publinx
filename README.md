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
4. [TODO](#todo)

# Installation
publinx is a uWSGI "app".

For the installation of uWSGI and Python 3 (at least 3.4), consult a guide you trust.

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
To publish the contents of a folder, add it to the configuration like you would with a regular file. Files beginning with a dot will not be displayed.

If you make all folders and files in this directory available, add `"recursive": true` to the setting. Although they are not displayed in the listing, files beginning with a dot are also made available through this.

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

To publish the contents of the root folder, use a dot as the key: `".": {}`. If you set the `recursive` rule, I highly recommend adding an exclusion for the configuration file, as publinx does not do this automatically.

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
A more advanced way of protecting your files is via HTTP authentication. publinx supports plain-text and hashed passwords using `crypt(3)`.
```json
{
    "passwordprotected.file": {
        "auth": {
            "plaintextuser": {
                "password": "plaintextpassword",
                "method": "plain"
            },
            "hasheduser": {
                "password": "$5$3FdNNXpxYY$2PTBfx8/Tug1Hy5O8wC45WInwE.XareJbLB4c.sPW60",
                "method": "crypt"
            }
        }
    }
}
```
The password protected file can now be accessed via HTTP authentication with `plaintextuser`/`plaintextpassword` or `hasheduser`/`password`.

To generate a password hash, you can use a `crypt(3)` implementation of your choice, like `mkpasswd`.

## Expiring links

To create a link that expires after a certain time, add a parameter `expires` with a ISO 8601 formatted date and time (or any other string that can be parsed by `dateutil.parser.parse`). After this time (on the server), the link won'be accessible any more and return 404.
```json
{
    "datedfile": {
        "expires": "2016-05-29T01:34:00+0200"
    }
}
```

## Comments

All other entries in the configuration file are ignored. To avoid possible future conflicts, I recommend adding comments with a `"_comment"` key.


# TODO

Ideas for the future that might be implemented when I need them. More ideas or implementations are welcome.

* Wildcard matching
* Access log