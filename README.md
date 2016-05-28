# publinx
A simple tool to make files available in an otherwise non-public directory


#Installation

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

Copy config.sample.py to config.py, change basedir to your data directory and, if needed, change the name of the cofig file.


#Configuring publinx:

All configuration takes place in the config file, which is basic JSON syntax.

## Simple file output
To simply return a file with the same path as it has in your directory, add it as a key to the config file:
```
{
    "simple-file.ext": {}
}
```
This file can now be accessed via `http://www.example.com/simple-file.ext`.

publinx also supports subfolders, so you can also add `folder/file.ext` to the config to return this file.

## Return a file on a different path
If you want to return a file from a different URL, use the public filename as the key and add a `path` parameter to the values:
```
{
    "public-filename.ext": {
        "path": "folder/hidden-filename.ext"
    }
}
```
Now, the file named `hidden-filename.ext` will be returned when `http://www.example.com/public-filename.ext` is requested.
