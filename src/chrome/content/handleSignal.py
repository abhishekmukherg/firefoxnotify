#!/usr/bin/env python

from  dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

import dbus
SESSION_BUS = dbus.SessionBus()

import gobject

NOTIFICATIONS_OBJECT = 'org.freedesktop.Notifications'
NOTIFICATIONS_PATH = '/org/freedesktop/Notifications'
NOTIFICATIONS_INTERFACE = 'org.freedesktop.Notifications'

class SignalHandler(object):
    def __init__(self, location, notification_id):
        self.loop = None
        self.location = location
        self.notification_id  = notification_id 

        notif = SESSION_BUS.get_object(NOTIFICATIONS_OBJECT, NOTIFICATIONS_PATH)

        # Connect the signals for actions
        print notif.connect_to_signal("ActionInvoked", self.actionInvokedHandler,
                dbus_interface=NOTIFICATIONS_INTERFACE)

        print notif.connect_to_signal("NotificationClosed",
                self.notificationClosedHandler,
                dbus_interface=NOTIFICATIONS_INTERFACE)

    def run(self):
        print "running"
        self.loop = gobject.MainLoop()
        self.loop.run()

    def notificationClosedHandler(self, id):
        print "Called notif handler"
        if id == self.notification_id:
            self.loop.quit()

    def actionInvokedHandler(self, id, key):
        print "Called action handler"
        if id == self.notification_id:
            if key == ACTIONS[0]:
                self.openFile()
            elif key == ACTIONS[2]:
                self.openDir()

    def openFile(self):
        os.execlp("xdg-open", "xdg-open", self.location)
    def openDir(self):
        os.execlp("xdg-open", "xdg-open", os.path.dirname(self.location))

def main():
    import sys
    if len(sys.argv) != 3:
        print >> sys.stderr, "Invalid number of arguments called"
        sys.exit(1)

    sig = SignalHandler(sys.argv[1], int(sys.argv[2]))
    sig.run()

if __name__=='__main__':
    main()
