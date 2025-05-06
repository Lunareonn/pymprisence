import dbus
import dbus.mainloop.glib

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()

player = bus.get_object("org.mpris.MediaPlayer2.sayonara",
                        "/org/mpris/MediaPlayer2")
properties = dbus.Interface(player, "org.freedesktop.DBus.Properties")


def get_metadata():
    metadata = properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")

    song_title = metadata.get("xesam:title", "Unknown Title")
    song_artist = metadata.get("xesam:artist", "Unknown Artist")
    song_length = round(metadata.get("mpris:length") / 1000000)

    return song_title, song_artist, song_length


def get_position():
    position = properties.Get("org.mpris.MediaPlayer2.Player", "Position")
    print(position)

    return round(position / 1000000)
