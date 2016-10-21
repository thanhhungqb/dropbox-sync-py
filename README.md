# Why need this script?

You need sync files/folders but just a central time, not need run as diamond.

Just upload/download some files/folders for working

Tiny resource of Disk, Ram, CPU...

This script required run manually (or as trigger)

If you want to real-time sync then please use Dropbox tool with full power.

# How to use

## Required:

- python3

- dropbox library for python (pip install dropbox)

- Access Token: see https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/

## Usage

1) open code, write your access token to TOKEN

2) make lst.txt file as format as sample file

3) Command

usage: dropbox-sync-py.py [-h] [-f FILE] {upload,download} ...

positional arguments:
  {upload,download}
    upload              upload files to Dropbox
    download            download files from Dropbox to local

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  list file, default is lst.txt in current directory
  
  
# TODO

- too many files/folders in Dropbox folder to download: just some of it can be download (work well with folder has more than 100 items)

- add feature to restore files

...