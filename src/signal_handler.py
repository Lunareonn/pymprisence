import dbus
import dbus.mainloop.glib
from dbus_connection import DBusSession
from gi.repository import GLib
import threading
from logs import logger


def start_signal_listener():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = DBusSession.get_bus()

    def on_properties_changed(interface, changed_properties, invalidated_properties):
        print("🎵 Properties changed:", changed_properties)

    bus.add_signal_receiver(
        handler_function=on_properties_changed,
        signal_name="PropertiesChanged",
        dbus_interface="org.freedesktop.DBus.Properties",
        path="/org/mpris/MediaPlayer2"
    )

    loop = GLib.MainLoop()
    loop.run()


def init_listener_thread():
    logger.debug("Starting listener thread")
    listener_thread = threading.Thread(target=start_signal_listener, daemon=True)
    listener_thread.start()
