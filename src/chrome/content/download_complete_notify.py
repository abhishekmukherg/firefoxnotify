#!/usr/bin/env python
"""
Opens a file in a galago aware environment to inform the user that a download
has completed
"""

import os
import pynotify
import pygtk
pygtk.require('2.0')
import gtk
import logging
from subprocess import Popen


OPEN_COMMAND = "xdg-open"
SUMMARY = "Firefox Download Complete"
BODY = "%s has been saved to %s"
HINTS = {"category": "transfer.complete"}


logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)


class GalagoNotRunningException(Exception):

    """
    Could not find galago server or Galago server did not behave as expected
    """

    pass


if not pynotify.init("FirefoxNotify"):
    raise GalagoNotRunningException


try:
    import xdg.IconTheme
except ImportError:
    APPICON = "firefox"
else:
    if xdg.IconTheme.getIconPath('firefox-3.0') is not None:
        APPICON = 'firefox-3.0'
    else:
        APPICON = 'firefox'


class FirefoxNotification(object):

    """
    Notification for a download complete from Firefox, essentially a wrapper
    around pynotify
    """

    def __init__(self, title, location):
        """Creates a Notification for Firefox"""
        self.title = title
        self.location = location

    def show(self):
        """Displays a notification for firefox.

        Adds actions open and opendir if available
        
        """
        self.notif = pynotify.Notification(SUMMARY,
                                      BODY % (self.title, self.location),
                                      APPICON,
                                      )
        self.notif.connect('closed', self._cleanup)

        caps = pynotify.get_server_caps()
        if caps is None:
            raise GalagoNotRunningException
        if 'actions' in caps:
            self.notif.add_action("open", "Open", self.open_file)
            self.notif.add_action("opendir", "Open Directory", self.open_directory)

        LOG.info("Displaying notification")
        if not self.notif.show():
            raise GalagoNotRunningException("Could not display notification")
        if 'actions' in caps:
            gtk.main()

    def _cleanup(self, notif=None, reason=None):
        LOG.info("Closing")
        gtk.main_quit()

    def open_file(self, notif=None, action_key=None):
        """Opens the file for the file given in self.location"""
        assert notif is None or notif == self.notif
        LOG.info(u"Opening file" + unicode(self.location))
        Popen([OPEN_COMMAND, self.location])
        self._cleanup()

    def open_directory(self, notif=None, action_key=None):
        """Opens the directory for the file given in self.location"""
        assert notif is None or notif == self.notif
        dir = os.path.dirname(self.location)
        LOG.info(u"Opening dir" + unicode(dir))
        Popen([OPEN_COMMAND, dir])
        self._cleanup()


def main():
    """Opens a notification in firefox

    sys.argv[1] should be the title and sys.argv[2] should be the location

    """
    import sys
    if len(sys.argv) != 3:
        print >> sys.stderr, "Invalid number of arguments called"
        sys.exit(1)
    notify = FirefoxNotification(sys.argv[1], sys.argv[2])
    notify.show()


if __name__ == '__main__':
    main()
