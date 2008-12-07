#!/usr/bin/env python
"""
Opens a file in a galago aware environment to inform the user that a download
has completed
"""

import dbusnotify
from os.path import dirname
from subprocess import Popen, call

FILENAME = ""
OPEN_COMMAND = "xdg-open"

def open_file():
    """Opens the file for the file given in the global FILENAME"""
    Popen([OPEN_COMMAND, FILENAME])
def open_dir():
    """Opens the directory for the file given in the global FILENAME"""
    Popen([OPEN_COMMAND, dirname(FILENAME)])

APPNAME = "Firefox"
APPICON = "firefox"
        
SUMMARY = "Firefox Download Complete"
BODY = "%s has completed downloading"
ACTIONS = {"Open": open_file, "Open Directory": open_dir}
HINTS = {"category": "transfer.complete"}

def open_notification(title, location):
    """Opens a download complete notification from Firefox"""
    global FILENAME
    FILENAME = location
    if call(["xdg-open", "--version"]) == 0:
        actions = ACTIONS
    else:
        actions = None
    notif = dbusnotify.GalagoNotification(SUMMARY,
                body=BODY % title,
                appname=APPNAME,
                appicon=APPICON,
                actions=actions,
                hints=HINTS,
                )
    notif.send()



def main():
    """Opens a notification in firefox

    sys.argv[1] should be the title and sys.argv[2] should be the location
    """
    import sys
    if len(sys.argv) != 3:
        print >> sys.stderr, "Invalid number of arguments called"
        sys.exit(1)
    open_notification(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
