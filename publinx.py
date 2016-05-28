import json
import os

from flask import Flask, send_from_directory

import config

publinx = Flask(__name__)

publinx.debug = True


@publinx.route('/<path:requested_file>')
def index(requested_file):
    # Load configuration
    with open(os.path.join(config.basedir, config.configfile)) as fp:
        filelist = json.load(fp)

    # Check if the requested file is not configured
    if requested_file not in filelist:
        return "File not found", 404

    # Finally serve the file
    if "path" in filelist[requested_file]:
        filename = filelist[requested_file]["path"]
    else:
        filename = requested_file

    return send_from_directory(config.basedir, filename)