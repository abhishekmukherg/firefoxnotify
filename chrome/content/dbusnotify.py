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

SESSION_BUS = dbus.SessionBus()
if SESSION_BUS == None:
    logging.critical("Could not connect to DBus Session")
    exit(1);

class FirefoxNotification(object):
    """
    A message from Firefox to a Galago compliant notification library.
    """
    def __init__(self, summary,
            body="",
            actions={},
            hints={"":0},
            actions_order=None):
        """
        Instantiates an object for sending a message. You must call send() when
        you  actually want to send the message.
        summary
        body    : pretty self explanatory
        action  : A dictionary of {string, callable} where string is the text
                  that should be displayed on the button and callable is a
                  function that takes no arguments
        hints   : directly passed to the notification server, see
                  http://www.galago-project.org/specs/notification/0.9/x344.html
        actions_order : If given, this should be a list of the keys of action in
                        the order you would like them displayed
        """
        self.id = id
        self.summary = summary
        self.body = body
        self.actions = actions
        self.actions_order = (actions_order or 
                              [ action for action in actions.keys() ])
        assert len(self.actions) == len(self.actions_order)
        self.hints = hints
        self.notification_id = None
    def send(self):
        """
        Sends notification to libnotify
        """
        notif = SESSION_BUS.get_object(NOTIFICATIONS_OBJECT, NOTIFICATIONS_PATH)
        # Get the actions into list format
        actions = [ x for x in enumerate(self.actions_order) ]
        actions_flat = []
        for act in actions:
            actions_flat.append(str(act[0]))
            actions_flat.append(act[1])
        notif_id = self.notification_id or 0
        self.notification_id = notif.Notify(APP_NAME,
                notif_id, APP_ICON, self.summary,
                self.body, actions_flat, self.hints,
                dbus.Int32(-1),
                dbus_interface=NOTIFICATIONS_INTERFACE)

        # Connect the signals for actions
        notif.connect_to_signal("ActionInvoked", self._signalHandler,
                dbus_interface=NOTIFICATIONS_INTERFACE)

        notif.connect_to_signal("NotificationClosed",
                self._notificationClosedHandler,
                dbus_interface=NOTIFICATIONS_INTERFACE)

        if len(self.actions):
            self._watch_for_signals()

    def _notificationClosedHandler(self, id, reason):
        """
        Callback for a closed notification, used to end the gobject loop
        """
        if id == self.notification_id:
            LOOP.quit()

    def _signalHandler(self, id, key):
        """
        Handler for when an action is invoked on the notification May not be
        relevant for all notification daemons
        """
        if id == self.notification_id:
            self.actions[self.actions_order[int(key)]]()
    def _watch_for_signals(self):
        LOOP.run()

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

    def foo():
        print "woo"

    # open notification
    f = FirefoxNotification(sys.argv[1], sys.argv[2], actions={"open":foo})
    f.send()

if __name__ == "__main__":
    main()
