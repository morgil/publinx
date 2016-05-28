import datetime
import json
import os

from flask import Flask, send_file, abort, render_template

import config

publinx = Flask(__name__)
publinx.debug = True


@publinx.route('/<path:request>')
def index(request):
    filename = get_real_path(request)

    if filename is None:
        abort(404)

    return send_file_or_directory(filename, request)


def get_real_path(request):
    with open(os.path.join(config.basedir, config.configfile)) as fp:
        filelist = json.load(fp)

    descriptor, rest = get_most_accurate_descriptor(request, filelist)

    if descriptor is None:
        return None

    if rest != '' and "recursive" in filelist[descriptor] and filelist[descriptor]["recursive"]:
        if "exclude" in filelist[descriptor]:
            print(filelist[descriptor]["exclude"])
            excluded, _ = get_most_accurate_descriptor(rest, filelist[descriptor]["exclude"])
            if excluded is not None:
                return None

    if "path" in filelist[descriptor]:
        filename = os.path.join(filelist[descriptor]["path"], rest)
    else:
        filename = os.path.join(descriptor, rest)

    if filename[-1] == '/':
        filename = filename[:-1]

    return filename


def get_most_accurate_descriptor(name, directory_list):
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


def send_file_or_directory(location, request):
    full = os.path.join(config.basedir, location)
    if not os.path.exists(full):
        raise IOError("Target file or directory does not exist: %s", full)
    if os.path.isdir(full):
        return send_directory(full, request)
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

