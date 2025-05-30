from logs import logger
import dbus


class DBusSession:
    _bus = None

    @classmethod
    def get_bus(cls):
        if cls._bus is None:
            cls._bus = dbus.SessionBus()
            logger.debug("Started DBus session.")
        return cls._bus
