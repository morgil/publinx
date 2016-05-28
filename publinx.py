import datetime
import json
import os

import dateutil.parser
from flask import Flask, send_file, abort, render_template, request

import config

publinx = Flask(__name__)
publinx.debug = True


@publinx.route('/', defaults={'request': ''})
@publinx.route('/<path:requested_path>')
def index(requested_path):
    """
    Entry point. Tries to resolve the requested file's real path, sends 404 if it's not available or gives control to
    a method sending the requested file or a directory listing.
    :param requested_path: Request path, provided by Flask
    :return: The sent file
    """
    filename = get_real_path(requested_path)

    if filename is None:
        abort(404)

    return send_file_or_directory(filename, requested_path)


def get_real_path(requested_path):
    """
    Parses the config file and returns the server-side path for the requested file.
    If the file can't or may not be accessed with this request, it returns None.
    :param requested_path: The request data (without a leading slash)
    :return: The server-side path
    """
    with open(os.path.join(config.basedir, config.configfile)) as fp:
        filelist = json.load(fp)

    if len(requested_path) > 0 and requested_path[-1] == '/':
        requested_path = requested_path[:-1]

    descriptor, rest = get_most_accurate_descriptor(requested_path, filelist)

    if descriptor is None:
        return None

    requested_entry = filelist[descriptor]

    if "expires" in requested_entry:
        expires = dateutil.parser.parse(requested_entry["expires"])
        print(expires)
        if expires < datetime.datetime.now(tz=expires.tzinfo):
            return None

    # If rest is not empty, there is an entry containing a part of the request. Let's check if requests to its
    # subfolders are allowed...
    if rest != '' and "recursive" in requested_entry and requested_entry["recursive"]:
        # ... and if there is an exclusion list, if the request is excluded.
        if "exclude" in requested_entry:
            excluded, _ = get_most_accurate_descriptor(rest, requested_entry["exclude"])
            if excluded is not None:
                return None

    # Check if the request maps to a different directory
    if "path" in requested_entry:
        filename = os.path.join(requested_entry["path"], rest)
    elif rest != '':
        filename = os.path.join(descriptor, rest)
    else:
        filename = descriptor

    # Is the file password protected? Return 404 to avoid leaking information on password protected files.
    # The information leak is probably vulnerable to timing side-channel attacks, but if you have to worry about that,
    # you shouldn't use this software.
    if "password" in requested_entry and request.args.get('password') != requested_entry['password']:
        return None

    return filename


def get_most_accurate_descriptor(name, directory_list):
    """
    Tries to find the entry in directory_list that matches the deepest directory in name (or the name, if it exists as
    an entry). Matching is performed using Pythons `in` operator, so that it searches the keys when directory_list is a
    dict and the values when it is a list.
    :param name: The file or directory name to look for.
    :param directory_list: The list contining all possible directories.
    :return: The deepest common directory/filename between name and directory_list's entries.
    """
    if name in directory_list:
        return name, ''

    head, tailpart = os.path.split(name)
    tail = tailpart
    while head != '':
        if head in directory_list:
            return head, tail
        head, tailpart = os.path.split(head)
        tail = os.path.join(tailpart, tail)

    return None, None


def send_file_or_directory(location, original_request):
    """
    Checks if the request points to a file or a directory and sends either the file or a directory listing.
    Raises IOError if the requested file does not exist (which means that the configuration file has an error)
    :param location: The location
    :param original_request: The requested url (for HTML links)
    :return: Flask's send_file or send_directory
    """
    full = os.path.join(config.basedir, location)
    if not os.path.exists(full):
        raise IOError("Target file or directory does not exist: %s", full)
    if os.path.isdir(full):
        return send_directory(full, original_request)
    if os.path.isfile(full):
        return send_file(full)


def send_directory(local_path, remote_url):
    """
    Constructs a directory listing
    :param local_path: The local (real) path of the files
    :param remote_url: The remote (requested) url. Used to generate links to the directory entries.
    :return: Flask's render_template
    """
    if not os.path.isdir(local_path):
        raise IOError("This is not a directory.")
    contents = listdir(local_path)
    return render_template('directory.html', directory=remote_url, contents=contents)


def listdir(path):
    contents = os.listdir(path)
    """
    Reads the entries of a given directory and returns them ordered by type (directories first) and name.
    Entries starting with a dot are ignored.
    :param path: The path
    :return: A list containing dicts for the entries, each with the keys name, human-readable size and timestamp
    """
    folderlist = []
    filelist = []

    def sizeof_fmt(num, suffix='B'):
        """
        Returns a human-readable representation of a file size. Code snippet from http://stackoverflow.com/a/1094933
        :param num: The file size
        :param suffix: The suffix
        :return:
        """
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    for entry in contents:
        if entry[0] == '.':
            continue
        if os.path.isdir(os.path.join(path, entry)):
            folderlist.append({
                "name": entry,
                "size": '',
                "timestamp": datetime.datetime.fromtimestamp(round(os.path.getmtime(os.path.join(path, entry))))
            })
        else:
            filelist.append({
                "name": entry,
                "size": sizeof_fmt(os.path.getsize(os.path.join(path, entry))),
                "timestamp": datetime.datetime.fromtimestamp(round(os.path.getmtime(os.path.join(path, entry))))
            })

    folderlist.sort(key=lambda e: e['name'])
    filelist.sort(key=lambda e: e['name'])
    return folderlist + filelist
