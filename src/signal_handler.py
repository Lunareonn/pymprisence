import dbus
import dbus.mainloop.glib
from dbus_connection import DBusSession
from gi.repository import GLib
import threading
from logs import logger
import asyncio
from presence import update_rpc, rpc_loop
from util import get_metadata, get_current_player, check_if_cover_cached, get_position, sanitize_player_name


async def start_signal_listener():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = DBusSession.get_bus()
    add_signal_receiver(bus)

    loop = GLib.MainLoop()
    loop.run()


def on_properties_changed():
    logger.debug("Properties changed")


def add_signal_receiver(bus):
    bus.add_signal_receiver(
        handler_function=on_properties_changed,
        signal_name="PropertiesChanged",
        dbus_interface="org.freedesktop.DBus.Properties",
        path="/org/mpris/MediaPlayer2"
    )


def thread_target():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_signal_listener())


async def init_listener_thread():
    logger.debug("Starting listener thread")
    listener_thread = threading.Thread(target=thread_target, daemon=True)
    listener_thread.start()
