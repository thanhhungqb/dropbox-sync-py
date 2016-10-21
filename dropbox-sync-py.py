"""
Backs up and restores a settings file to Dropbox.
This is an example app for API v2. 
required: pip install dropbox
"""

import sys
import os
from os import listdir
from os.path import isfile, join
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

# Add OAuth2 access token here. 
# You can generate one for yourself in the App Console.
# See <https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/>
TOKEN = ''

# Uploads contents of LOCALFILE to Dropbox
def uploadFile(LOCALFILE, BACKUPPATH):
    with open(LOCALFILE, 'rb') as f:
        # We use WriteMode=overwrite to make sure that the settings in the file
        # are changed on upload
        print("Uploading F " + LOCALFILE + " to Dropbox as " + BACKUPPATH + "...")
        try:
            dbx.files_upload(f, BACKUPPATH, mode=WriteMode('overwrite'))
        except ApiError as err:
            # This checks for the specific error where a user doesn't have
            # enough Dropbox space quota to upload this file
            if (err.error.is_path() and
                    err.error.get_path().error.is_insufficient_space()):
                pass
            elif err.user_message_text:
                print(err.user_message_text)
            else:
                print(err)

def uploadFolder(folder, dfolder):
    print("Uploading " + folder + " to Dropbox " + dfolder)
    if os.path.isdir(folder):
        for f in listdir(folder):
            uploadFolder(join(folder,f), join(dfolder, f))
    elif os.path.isfile(folder):
        uploadFile(folder, dfolder)
    else:
        print(folder, ' is not found')

# load from files.txt, each line have "file dropbox_file" seperated by one TAB
# file maybe file or folder, base on it with call uploadFolder of backup
def backupPackage(fname='lst.txt'):
    with open(fname, 'r') as f:
        for line in f:
            line = line.partition('#')[0]
            line = line.rstrip()
            lst = line.strip().split("\t")
            if len(lst)>1:
                uploadFolder(lst[0], lst[1])

# same as backupPackage
def downloadPackage(fname='lst.txt'):
    with open(fname, 'r') as f:
        for line in f:
            line = line.partition('#')[0]
            line = line.rstrip()
            lst = line.strip().split("\t")
            if len(lst)>1:
                downloadFolder(lst[1], lst[0])

def downloadFolder(dfolder, folder):
    print('downloading ', dfolder, ' to ', folder)
    try:
        dbx.files_download_to_file(folder, dfolder)
    except:
        os.makedirs(folder, exist_ok=True)
        d = dbx.files_list_folder(dfolder)	# TODO if has_more=True then have to continue until False (big number of files)
        for f in d.entries:
            downloadFolder(f.path_display, join(folder, f.name))

# Restore the local and Dropbox files to a certain revision
def restore(rev=None):
    # Restore the file on Dropbox to a certain revision
    print("Restoring " + BACKUPPATH + " to revision " + rev + " on Dropbox...")
    dbx.files_restore(BACKUPPATH, rev)

    # Download the specific revision of the file at BACKUPPATH to LOCALFILE
    print("Downloading current " + BACKUPPATH + " from Dropbox, overwriting " + LOCALFILE + "...")
    dbx.files_download_to_file(LOCALFILE, BACKUPPATH, rev)

# Look at all of the available revisions on Dropbox, and return the oldest one
def select_revision():
    # Get the revisions for a file (and sort by the datetime object, "server_modified")
    print("Finding available revisions on Dropbox...")
    revisions = sorted(dbx.files_list_revisions(BACKUPPATH, limit=30).entries,
                       key=lambda entry: entry.server_modified)

    for revision in revisions:
        print(revision.rev, revision.server_modified)

    # Return the oldest revision (first entry, because revisions was sorted oldest:newest)
    return revisions[0].rev

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='list file, default is lst.txt in current directory',default='lst.txt')
    subparsers=parser.add_subparsers(dest='action')
    upload_parser = subparsers.add_parser('upload', help="upload files to Dropbox")
    download_parser = subparsers.add_parser('download', help="download files from Dropbox to local")
    
    args = parser.parse_args()
    
    # Check for an access token
    if (len(TOKEN) == 0):
        sys.exit("ERROR: Looks like you didn't add your access token. Open up backup-and-restore-example.py in a text editor and paste in your token in line 14.")

    # Create an instance of a Dropbox class, which can make requests to the API.
    print("Creating a Dropbox object...")
    dbx = dropbox.Dropbox(TOKEN)

    # Check that the access token is valid
    try:
        dbx.users_get_current_account()
    except AuthError as err:
        sys.exit("ERROR: Invalid access token; try re-generating an access token from the app console on the web.")

    # Create a backup of the current settings file
    if args.action == 'upload':
        backupPackage(args.file)
    elif args.action == 'download':
        downloadPackage(args.file)
    else:
        print('use command upload/download')

    # Restore the local and Dropbox files to a certain revision
    #to_rev = select_revision()
    #restore(to_rev)

    print("Done!")

