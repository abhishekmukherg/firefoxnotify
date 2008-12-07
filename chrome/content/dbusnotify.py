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

from  dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

# Galago spec
NOTIFICATIONS_OBJECT = 'org.freedesktop.Notifications'
NOTIFICATIONS_PATH = '/org/freedesktop/Notifications'
NOTIFICATIONS_INTERFACE = 'org.freedesktop.Notifications'
CLOSED_REASON = ["", "expired", "dismissed", "CloseNotification", "undefined"]

SESSION_BUS = dbus.SessionBus()
if SESSION_BUS == None:
    logging.critical("Could not connect to DBus Session")
    exit(1)

class GalagoNotification(object):
    """
    A message from Firefox to a Galago compliant notification library.
    """
    def __init__(self, summary,
            body=None,
            appname=None,
            appicon=None,
            actions=None,
            hints=None,
            actions_order=None,
            default_action=None,
            closed_action=None):
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
        default_action: Default action to perform if the message is just
                        clicked
        closed_action : callable if the notification is closed, should take one
                        one argument, which will be a string from CLOSED_REASON
        """
        self.summary = summary
        self.body = body
        self.appname = (appname or "")
        self.appicon = (appicon or "")
        self.actions = (actions or {})
        self.actions_order = (actions_order or 
                              [ action for action in self.actions.keys() ])
        assert len(self.actions) == len(self.actions_order)
        self.default = default_action
        self.hints = (hints or {"":0})
        self.closed_action = closed_action
        self._notification_id = None
        self._loop = None
    def send(self):
        """ Sends notification to libnotify """
        notif = SESSION_BUS.get_object(NOTIFICATIONS_OBJECT, NOTIFICATIONS_PATH)
        # Get the actions into list format
        actions = [ x for x in enumerate(self.actions_order) ]
        actions_flat = []
        for act in actions:
            actions_flat.append(str(act[0]))
            actions_flat.append(act[1])
        notif_id = self._notification_id or 0
        self._notification_id = notif.Notify(self.appname,
                notif_id, self.appicon, self.summary,
                self.body, actions_flat, self.hints,
                dbus.Int32(-1),
                dbus_interface=NOTIFICATIONS_INTERFACE)

        # Connect the signals for actions
        notif.connect_to_signal("ActionInvoked", self._action_invoked,
                dbus_interface=NOTIFICATIONS_INTERFACE)

        notif.connect_to_signal("NotificationClosed",
                self._notification_closed_handler,
                dbus_interface=NOTIFICATIONS_INTERFACE)

        # Only watch if we have actions
        self._watch_for_signals()

    def _notification_closed_handler(self, notif_id, reason):
        """
        Callback for a closed notification, used to end the gobject loop
        """
        if notif_id == self._notification_id:
            self._loop.quit()
        if self.closed_action:
            assert reason > 0
            self.closed_action(CLOSED_REASON[reason])

    def _action_invoked(self, notif_id, key):
        """
        Handler for when an action is invoked on the notification May not be
        relevant for all notification daemons
        """
        if notif_id == self._notification_id:
            if key == "default":
                if self.default:
                    self.actions[self.default]()
            else:
                self.actions[self.actions_order[int(key)]]()
    def _watch_for_signals(self):
        """
        Called so that our program does not end until we get a
        closed_notification
        """
        if self._loop == None:
            self._loop = gobject.MainLoop()
        self._loop.run()

def main():
    """Takes two arguments from sys.argv and creates a notification with argv[1]
    as the summary and argv[2] as the body"""
    import sys
    if len(sys.argv) != 3:
        logging.warning("%s called with invalid number of arguments" %
                                                        sys.argv[0])
        logging.warning("Arguments were: %s" % sys.argv)
        sys.exit(1)

    # open notification
    notif = GalagoNotification(sys.argv[1], sys.argv[2])
    notif.send()

if __name__ == "__main__":
    main()
