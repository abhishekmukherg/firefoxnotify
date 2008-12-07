#!/usr/bin/env python
'''
Sends a DBus Notification to freedesktop's interface.

Abhishek Mukherjee <linkinpark342@gmail.com>

Credit to 
 * dot_j <dot_j@mumbles-project.org>
for his DBus Notifications Extension
<https://addons.mozilla.org/en-US/firefox/addon/5617>
which was used extensively as an example for this
'''
import dbus
import logging
import gobject
import sys, os
from subprocess import call

# Use gtk's main loop... since firefox needs it anyways...
from  dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
LOOP = gobject.MainLoop()

# Galago spec
NOTIFICATIONS_OBJECT = 'org.freedesktop.Notifications'
NOTIFICATIONS_PATH = '/org/freedesktop/Notifications'
NOTIFICATIONS_INTERFACE = 'org.freedesktop.Notifications'

# Message Properties
APP_NAME = "Firefox"
APP_ICON = "firefox"
SUMMARY = "Firefox Download Complete"
BODY = "%s has completed downloading"
ACTIONS = ["open", "Open File", "opendir", "Open Directory"]
HINTS = {"category": "transfer.complete"}

SESSION_BUS = dbus.SessionBus()
assert(SESSION_BUS != None)

class FirefoxDbus(object):
    """
    Creates a message from Firefox to a galago compliant notification library
    """
    def __init__(self, title, location):
        self.id = id
        self.title = title
        self.location = location
        self.notification_id = None
    def downloadComplete(self, actionsEnabled=True):
        """
        Sends a signal that download for title has completed
        """
        notif = SESSION_BUS.get_object(NOTIFICATIONS_OBJECT, NOTIFICATIONS_PATH)
        if actionsEnabled:
            actions = ACTIONS
        else:
            actions = [""]

        self.notification_id = notif.Notify(APP_NAME,
                dbus.UInt32(0),
                APP_ICON,
                SUMMARY,
                BODY % self.title,
                actions,
                HINTS,
                dbus.Int32(-1),
                dbus_interface=NOTIFICATIONS_INTERFACE)

        # Connect the signals for actions
        notif.connect_to_signal("ActionInvoked", self.signalHandler,
                dbus_interface=NOTIFICATIONS_INTERFACE)

        notif.connect_to_signal("NotificationClosed",
                self.notificationClosedHandler,
                dbus_interface=NOTIFICATIONS_INTERFACE)

    def notificationClosedHandler(self, id):
        """
        Callback for a closed notification, used to end the gobject loop
        """
        if id == self.notification_id:
            LOOP.quit()

    def signalHandler(self, id, key):
        """
        Handler for when an action is invoked on the notification May not be
        relevant for all notification daemons
        """
        if id == self.notification_id:
            if key == ACTIONS[0]:
                self.openFile()
            elif key == ACTIONS[2]:
                self.openDir()

    def openFile(self):
        """
        Opens the file using xdg-open. You need xdg-utils for this to work.
        """
        os.execlp("xdg-open", "xdg-open", self.location)
    def openDir(self):
        """
        Opens the file's directory using xdg-open. You need xdg-utils for this
        to work.
        """
        os.execlp("xdg-open", "xdg-open", os.path.dirname(self.location))

def main():
    if len(sys.argv) != 3:
        logging.warning("%s called with invalid number of arguments" % sys.argv[0])
        logging.warning("Arguments were: %s" % sys.argv)
        sys.exit(1)

    # Find out if we have ability to open files using portland project
    try:
        retval = call(["xdg-open", "--version"])
    except:
        retval = -1

    if retval == 0:
        actionsEnabled = True
    else:
        actionsEnabled = False

    # open notification
    f = FirefoxDbus(title=sys.argv[1], location=sys.argv[2])
    f.downloadComplete(actionsEnabled)

    # start signal handler loop
    LOOP.run()

if __name__ == "__main__":
    main()
