from util import bus


def on_seeked(position):
    print("New position:", position)


async def listener():
    bus.add_signal_receiver(
        on_seeked,
        signal_name="Seeked",
        dbus_interface="org.mpris.MediaPlayer2.Player"
    )
