import dbus
# import dbus.mainloop.glib


class DBusSession:
    _bus = None

    @classmethod
    def get_bus(cls):
        if cls._bus is None:
            cls._bus = dbus.SessionBus()
        return cls._bus
