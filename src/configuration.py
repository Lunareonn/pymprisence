import toml
import os

config_folder = os.path.join(os.path.expanduser("~"), ".config")


async def check_config() -> bool:
    if os.path.isfile(os.path.join(config_folder, "pymprisence", "config.toml")):
        return True
    else:
        print(os.path.join(config_folder, "pymprisence", "config.toml"))
        return False


async def generate_config():
    if await check_config() is True:
        print("config file found")
        return
    else:
        print("config file not found")
        if not os.path.isdir(os.path.join(config_folder, "pymprisence")):
            os.makedirs(os.path.join(config_folder, "pymprisence"))

        with open("./config/config.default.toml", "r+") as dcfg:
            default_config = toml.load(dcfg)
        with open(os.path.join(config_folder, "pymprisence", "config.toml"), "w+") as cfg:
            toml.dump(default_config, cfg)
