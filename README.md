# publinx
A simple tool to make files available in an otherwise non-public directory. Works with nginx+uWSGI+Python+Flask.

I made this because I [synchronize](https://www.syncthing.net/) my data to my server and sometimes want other people to access certain files.
 With this tool, I can selectively give out access to files by simply editing a JSON file in my synchronized directory.

Right now, it is still incomplete and should not be considered secure.

This project is licensed under GPLv3, so please create beautiful things with it.

#Table of contents
1. [Installation (short)](#installation-short)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Creating public links](#creating-public-links)

#Installation (short)
publinx is a uWSGI "app". Install and configure uWSGI as you like it. Install the Python module Flask. Point uWSGI to `module=publinx` and `callable=publinx`.

Copy the config.sample.py to config.py and set the variables. The `configfile` is expected to be found inside the `basedir`.

Look at `.publinx.sample.json` or the configuration section in this file for how to create public links.

#Installation

These installation instructions have been adapted from [http://www.markjberger.com/flask-with-virtualenv-uwsgi-nginx/](http://www.markjberger.com/flask-with-virtualenv-uwsgi-nginx/) and should be followed with caution. You should rather read the official installation instructions and adapt them for your needs.

Install python and flask.
```
sudo apt-get install build-essential python-dev python-pip

cd /my/directory
git clone git@github.com:morgil/publinx.git
cd publinx

pip install flask

sudo apt-get install nginx uwsgi uwsgi-plugin-python
```

Prepare a file socket (or use a TCP socket if you like):
```
cd /tmp/
touch publinx.sock
sudo chown www-data publinx.sock
```
Configure nginx:
```
cd /etc/nginx/sites-available
touch publinx
```
Put the following into publinx:
```
server {
    listen 80;
    server_tokens off;
    server_name www.example.com;

     location / {
         include uwsgi_params;
         uwsgi_pass unix:/tmp/publinx.sock;
     }
}
```
And link the file:
```
cd ../sites-enabled/
sudo ln -s ../sites-available/publinx publinx
```
Configure uWSGI:
```
cd /etc/uwsgi/apps-available
touch publinx.ini
```
Put the following into publinx.ini:
```
[uwsgi]
vhost = true
socket = /tmp/publinx.sock
chdir = /my/directory/publinx
module = publinx
callable = publinx
```
Link the file and reload the config:
```
cd ../apps-enabled/
sudo ln -s ../apps-available/publinx.ini publinx.ini

sudo service nginx restart
sudo service uwsgi restart
```


#Configuration:
Copy config.sample.py to config.py, change basedir to your data directory and, if needed, change the name of the config file.


#Creating public links

All configuration takes place in the config file, which is basic JSON syntax.

Note that there are no checks for valid but stupid configurations. If you want to make your home directory or your config file publicly available, I won't stop you.

## Simple file output
To simply return a file with the same path as it has in your directory, add it as a key to the config file:
```json
{
    "simple-file.ext": {}
}
```
This file can now be accessed via `http://www.example.com/simple-file.ext`.

publinx also supports subfolders, so you can also add `folder/file.ext` to the config to return this file.

## Returning a file on a different path
If you want to return a file from a different URL, use the public filename as the key and add a `path` parameter to the values:
```json
{
    "public-filename.ext": {
        "path": "folder/hidden-filename.ext"
    }
}
```
Now, the file at `folder/hidden-filename.ext` will be returned when `http://www.example.com/public-filename.ext` is requested.

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
Now, you can only access this file via http://www.example.com/secret.file?password=hunter2. If the wrong password or no password is given, it acts as if the file does not exist and returns a 404 error to avoid obviously leaking information.