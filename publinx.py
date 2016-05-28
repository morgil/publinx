import datetime
import json
import os

from flask import Flask, send_file, abort, render_template

import config

publinx = Flask(__name__)
publinx.debug = True


@publinx.route('/<path:requested_file>')
def index(requested_file):
    # Load configuration
    with open(os.path.join(config.basedir, config.configfile)) as fp:
        filelist = json.load(fp)

    # Check if the requested file is in the config file
    if requested_file not in filelist:
        directory, _ = os.path.split(requested_file)
        while directory != '':
            if directory in filelist and "recursive" in filelist[directory] and filelist[directory]["recursive"]:
                break
            directory, _ = os.path.split(directory)
        else:
            abort(404)

    # Finally serve the file (if the file is in a recursively marked directory, it's still not in filelist
    if requested_file in filelist and "path" in filelist[requested_file]:
        filename = filelist[requested_file]["path"]
    else:
        filename = requested_file

    print(filename)

    return send_file_or_directory(config.basedir, filename)


def send_file_or_directory(basedir, location):
    full = os.path.join(basedir, location)
    if not os.path.exists(full):
        raise IOError("Target file or directory does not exist.")
    if os.path.isdir(full):
        return send_directory(full, location)
    if os.path.isfile(full):
        return send_file(full)


def send_directory(full, title):
    if not os.path.isdir(full):
        raise IOError("This is not a directory.")
    contents = listdir(full)
    return render_template('directory.html', directory=title, contents=contents)


def listdir(path):
    """
    Reads the entries of a given directory and returns them ordered by type and name
    :param path: The path
    :return: A list containing dicts for the entries, each with the keys name, size (human-readable) and timestamp
    """
    contents = os.listdir(path)
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

